# handle all routing things

# not sure what the imports should be but these seem to work?
import jsonpickle
from functools import wraps
from datetime import datetime
from flask import render_template, flash, redirect, request, url_for, session
from application import application
from application.forms import LoginForm, CheckinManager, MemberManager, MemberAddForm, MemberInfoHandler, AuthenticateForm, ClubhouseManager, ClubhouseAddForm, ClubhouseInfoHandler
from flask_babel import lazy_gettext as _l
from flask_login import current_user, login_user, logout_user
from werkzeug.urls import url_parse
from wtforms.validators import DataRequired
from .db import *
from .plot import *
from .models import *

# function for two-level authentication
# also handles clubhouse impersonation
def login_required(access="basic", impersonate = False):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated: # user not logged in
                return login_manager.unauthorized()
            # access is either basic or admin
            if current_user.access != access and access != "basic":
                flash(_l("Insufficient credentials."))
                return redirect('/')
            # club_id is always in session for a clubhouse account
            if impersonate and 'club_id' not in session: # impersonation not met
                flash(_l("Please select a clubhouse to impersonate."))
                return redirect('/admin/clubhouseselect')
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def fresh_login_required(access="basic", impersonate = False):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            if current_user.access != access and access !="basic":
                flash(_l("Insufficient credentials."))
                return redirect('/')
            if not session['fresh']:
                return login_manager.needs_refresh()
            if impersonate and 'club_id' not in session: # same logic as above
                flash(_l("Please select a clubhouse to impersonate."))
                return redirect('/admin/clubhouseselect')
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

### homepages

@application.route('/')
def home():
    return render_template('index.html')

@application.route('/home') # to make it easier to route based on user access
@fresh_login_required()
def reroute_home():
    if current_user.access == 'admin':
        return redirect('/admin')
    return redirect('/clubhouse')

@application.route('/clubhouse')
@fresh_login_required(impersonate = True)
def club_home():
    return render_template('/clubhouse/home.html')

@application.route('/admin')
@fresh_login_required(access="admin")
def admin_home():
    return render_template('/admin/home.html')

# view data pages
@application.route('/clubhouse/view', methods=['GET','POST'])
@fresh_login_required(impersonate = True)
def coord_view():
    # the time_range will return the number of days to be considered
    # [1, 7, 30, 365] corresponding to day, week, month, year
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    # 0 is meant to be raw data, e.g. number of people on each day
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week")), (3, _l("Statistics")), (4, _l("Number of Members"))]
    if request.method == 'POST':
        # extract relevant information
        cur_range = request.form['range']
        cur_format = request.form['format']
        # pass cur_range, cur_format to template
        # to keep them displayed on the page (minimize confusion)
        return render_template('/clubhouse/view.html', time_ranges=time_ranges, data_format=data_format, plot=plot(cur_range, cur_format, session['club_id']), cur_range =int(cur_range), cur_format = int(cur_format))
    if request.method == 'GET':
        # default cur_range, cur_format to be the first in the list
        return render_template('/clubhouse/view.html', time_ranges=time_ranges, data_format=data_format, cur_range = time_ranges[0][0], cur_format = data_format[0][0])

@application.route('/admin/view', methods=['GET', 'POST'])
@fresh_login_required(access="admin")
def admin_view():
    # copied from coord_view
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week")), (3, _l("Statistics")), (4, _l("Number of Members"))]
    if request.method == 'POST':
        cur_range = request.form['range']
        cur_format = request.form['format']
        return render_template('/admin/view.html', time_ranges=time_ranges, data_format=data_format, plot=plot(cur_range, cur_format), cur_range=int(cur_range), cur_format=int(cur_format))
    if request.method == 'GET':
        return render_template('/admin/view.html', time_ranges=time_ranges, data_format=data_format, cur_range = time_ranges[0][0], cur_format = data_format[0][0])

# logins and logouts, account management

# logout routing
@application.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# basic login form, it doesn't post anything yet
@application.route('/login', methods=['GET','POST'])
def login():
    if current_user.is_authenticated: # already logged in, redirect based on account type
        if current_user.access == "admin":
            return redirect('/admin')
        return redirect('/clubhouse')
    form = LoginForm()
    if form.validate_on_submit():
        # read user input to form
        username = request.form['user']
        password = request.form['password']
        u_id = get_id_from_username(username)
        if u_id: # valid user
            user = User(u_id) # generate user object
            if user.check_password(password): # login success
                login_user(user, remember=form.remember.data)
                session['fresh'] = True # manually set fresh session
                # determine whether this user prefers last, first or first last
                session['last_name_first'] = user.last_name_first
                # redirect based on user status
                if user.access == "admin":
                    # reset stored club id and impersonation name
                    if 'club_id' in session:
                        session.pop('club_id')
                    if 'impersonation' in session:
                        session.pop('impersonation')
                    return redirect('/admin')
                # otherwise this user is a clubhouse coordinator
                session['club_id'] = get_club_id_from_user(user_id=u_id) # store club id in use
                return redirect('/clubhouse')
        # display that credentials are incorrect
        flash(_l("Username/password combination incorrect."))
        return redirect('/login')
    return render_template('login.html', form=form, refresh = False)

# page for reauthentication
@application.route('/reauthenticate', methods=['GET','POST'])
@login_required()
def reauthenticate():
    form = AuthenticateForm()
    if form.validate_on_submit():
        # read user input to form
        password = request.form['password']
        if current_user.check_password(password): # login success
            session['fresh'] = True # session is now fresh
            # determine next page
            next_page = request.args.get('next')
            if not next_page or url_parse(next_page).netloc != '':
                # redirect based on user status
                if current_user.access == "admin":
                    next_page = '/admin'
                else:
                    next_page = '/clubhouse'
            return redirect(next_page)
        # display that credentials are incorrect
        flash(_l("Incorrect password."))
        return redirect('/reauthenticate')
    return render_template('login.html', form=form, refresh = True)

@application.route('/account', methods=['GET','POST'])
@fresh_login_required()
def edit_account_details(): # change password, edit display name
    # pre-populate form fields
    working_id = current_user.id # login id
    if current_user.access == "admin":
        # must take the form full_name, short_name, join_date, name_display, username
        load_info = (None, None, None, current_user.last_name_first, current_user.username)
    else:
        load_info = get_clubhouse_from_id(session['club_id'], field=None) + (current_user.username,)
    # still use wrapper of ClubhouseInfoHandler
    handler = ClubhouseInfoHandler(load_info)
    form = handler.form
    if current_user.access == "admin": # for form validation later
        form.full_name.validators = []
        form.short_name.validators = []
        form.password.validators = [DataRequired()]
    # handle POST request
    if request.method == 'POST':
        if "cancel_btn" in request.form: # cancel update
            return redirect('/home')
        # require password before doing anything
        if current_user.check_password(request.form['old_password']):
            if form.validate_on_submit():
                if len(request.form['password']) > 0: # update password
                    update_password(working_id, request.form['password'])
                # update clubhouse name and info
                if current_user.access == "clubhouse":
                    update_club_info(session['club_id'], request.form['full_name'], request.form['short_name'], form.display_by_last.data)
                    # reset session field in case this changed
                    session['last_name_first'] = form.display_by_last.data
                flash(_l("Updated successfully."))
                return redirect('/home')
        else:
            flash(_l("Incorrect password."))
    return render_template('account.html', form=form)

# rest of app routes for clubhouse home page

# add new member
@application.route('/clubhouse/addmember', methods=['GET','POST']) # might need a method -- better to make html name informative if different?
@fresh_login_required(impersonate = True)
def create_member():
    form = MemberAddForm()
    # default join date
    form.join_date.render_kw = {'value': datetime.now().date()}
    if request.method == 'POST':
        if "cancel_btn" in request.form:
            return redirect('/clubhouse/members')
        elif form.validate_on_submit():
            message, added_mem_id = add_member(session['club_id'], convert_form_to_dict(request.form, ["csrf_token", "add_btn"]))
            flash(message)
            session['edit_member_id'] = added_mem_id
            return redirect('/clubhouse/editmember') # shows the posted data of newly created member
    return render_template('/clubhouse/edit.html', form=form, new_member=True)

@application.route('/clubhouse/members', methods=['GET','POST'])
@fresh_login_required(impersonate = True)
def manage_members():
    club_id = session['club_id']
    form_manager = MemberManager(club_id, session['last_name_first'])
    if request.method == "POST":
        if "new_member" in request.form: # add new member
            return redirect('/clubhouse/addmember')
        if form_manager.member_form.validate_on_submit(): # confirm member selected for edit
            # temporarily store member id
            session['edit_member_id'] = int(request.form['memberselect'])
            return redirect('/clubhouse/editmember')
    return render_template('/clubhouse/membership.html', form=form_manager.member_form)

@application.route('/clubhouse/editmember',methods=['GET','POST'])
@fresh_login_required(impersonate = True)
def edit_member_info():
    if 'edit_member_id' not in session:
        # this page is not accessible without choosing a member to edit
        return redirect('/clubhouse/members')
    club_id = session['club_id']
    mem_id = session['edit_member_id']
    if request.method == 'POST':
        if "cancel_btn" in request.form: # cancel the updates
            session.pop('edit_member_id')
            return redirect('/clubhouse/members')
        if "delete_btn" in request.form: # delete member from active members
            flash(delete_specific_member(club_id, mem_id)) # delete from db, return success/error
            session.pop('edit_member_id') # clear stored id
            return redirect('/clubhouse/members')
        # otherwise update info
        if "update_btn" in request.form:
            flash(edit_member(club_id, mem_id, convert_form_to_dict(request.form, ["csrf_token", "update_btn"])))
            # clear stored info
            session.pop('edit_member_id')
            return redirect('/clubhouse/editmember')
    # handle get portion - viewing info
    if request.method == "GET":
        # pull stored information
        handle = MemberInfoHandler(get_specific_member(club_id, mem_id))
        return render_template('/clubhouse/edit.html', form=handle.form, new_member=False, plot_month=plot_by_member(club_id, mem_id, 30), plot_year=plot_by_member(club_id, mem_id, 365), plot_time=plot('365', '1', club_id, mem_id), plot_weekday=plot('365', '2', club_id, mem_id))

# check-in page, main functionality of website
@application.route('/clubhouse/checkin', methods=['GET','POST'])
@login_required(impersonate = True)
def checkin_handler():
    # manually set session to stale
    session['fresh'] = False
    if request.method == "GET":
        # get checkin manager for this specific clubhouse
        club_id = session['club_id']
        testform = CheckinManager(club_id, session['last_name_first'])
        # enable_auto_checkout(club_id) # should only create db event once to set up auto_checkout
    if request.method == "POST":
        # deserialize testform and rebind fields
        testform = jsonpickle.decode(session['testform'])
        testform.check_in_form.__init__()
        testform.setfields()
        # TODO: find a better solution to form resubmission error
        try:
            if "check_in" in request.form and "check_in_id" in request.form: # check-in button clicked
                testform.checkin_member(int(request.form["check_in_id"]))
            elif "check_out_id" in request.form: # check-out button
                testform.checkout_member(int(request.form["check_out_id"]))
            elif "all_check_out" in request.form:
                return redirect('/clubhouse/checkout')
            # serialize for persistence
            session['testform'] = jsonpickle.encode(testform)
            return render_template('/clubhouse/checkin.html',form=testform.check_in_form)
        except ValueError: # cheating way to handle form resubmission
            return redirect('/clubhouse/checkin')
    session['testform'] = jsonpickle.encode(testform) # serialize, persistence
    return render_template('/clubhouse/checkin.html',form=testform.check_in_form)

# mass checkout
@application.route('/clubhouse/checkout')
@fresh_login_required(impersonate = True)
def mass_checkout():
    club_id = session['club_id']
    checkins = get_checked_in_members(club_id)
    for mem_id, mem_name in checkins:
        add_checkout(mem_id, club_id)
    flash(_l("Checked out all members."))
    return redirect('/clubhouse/checkin')

# rest of app routes for admin home page

# largely copied from clubhouse/members
@application.route('/admin/clubhouses', methods=['GET','POST'])
@fresh_login_required(access="admin")
def manage_clubhouses():
    # create form from wrapper class to force refresh database pull
    form = ClubhouseManager().club_form
    if request.method == "POST":
        if "new_clubhouse" in request.form: # add new clubhouse
            return redirect('/admin/addclubhouse')
        if form.validate_on_submit():
            if "view" in request.form: # impersonate clubhouse
                session['club_id'] = int(request.form['clubhouseselect'])
                session['impersonation'] = get_clubhouse_from_id(session['club_id'], "full_name")
                return redirect('/clubhouse')
            # otherwise edit button pressed, edit clubhouse
            # get and save id of clubhouse being edited
            session['edit_club_id'] = int(request.form['clubhouseselect'])
            return redirect('/admin/editclubhouse')
    return render_template('/admin/clubhouses.html', form=form)

# page to select clubhouse to impersonate
# basically the same as above but with fewer things to handle
@application.route('/admin/clubhouseselect', methods=['GET','POST'])
@fresh_login_required(access="admin")
def choose_clubhouse():
    form = ClubhouseManager().club_form
    if form.validate_on_submit():
        session['club_id'] = int(request.form['clubhouseselect'])
        session['impersonation'] = get_clubhouse_from_id(session['club_id'], "full_name")
        return redirect('/clubhouse')
    return render_template('/admin/clubhouses.html', form=form, select_only = True)

@application.route('/admin/editclubhouse', methods=['GET','POST'])
@fresh_login_required(access="admin")
def edit_clubhouse_info():
    if 'edit_club_id' not in session: # can only access this page if clubhouse selected
        return redirect('/admin/clubhouses')
    # retrieve login id
    working_id = get_user_id_from_club(session['edit_club_id'])
    # retrieve username
    u_name = get_user_from_id(working_id)[1]
    club_info = get_clubhouse_from_id(session['edit_club_id'], field=None)
    # clubhouse preference for name_display does not get changed here
    load_info = club_info[:-1] + (None, u_name)
    handler = ClubhouseInfoHandler(load_info)
    form = handler.form
    if request.method == 'POST':
        if "cancel_btn" in request.form: # cancel update
            session.pop('edit_club_id')
            return redirect('/admin/clubhouses')
        elif "delete_btn" in request.form: # delete clubhouse
            flash(delete_clubhouse(session['edit_club_id'])) # delete from db
            if 'club_id' in session and session['club_id'] == session['edit_club_id']:
                session.pop('club_id') # remove from memory if impersonating clubhouse is deleted
            return redirect('/admin/clubhouses')
        elif form.validate_on_submit():
            # update password
            if len(request.form['password']) > 0:
                update_password(working_id, request.form['password'])
            # update everything else
            # join_date should not get updated in practice
#            join_date = None
#            if 'join_date' in request.form: # in practice this should not happen
#                join_date = request.form['join_date']
            update_club_info(session['edit_club_id'], request.form['full_name'], request.form['short_name'])
            session.pop('edit_club_id') # remove club_id from memory
            flash(_l("Updated successfully."))
            return redirect('/admin/clubhouses')
    return render_template('/admin/change.html', form=form, clubhouse_name=load_info[0])

@application.route('/admin/addclubhouse', methods=['GET','POST'])
@fresh_login_required(access="admin")
def admin_clubhouses():
    form = ClubhouseAddForm()
    form.join_date.render_kw = {'value': datetime.now().date()}
    if request.method == "POST":
        if "cancel_btn" in request.form: # cancel clubhouse add
            return redirect('/admin/clubhouses')
        elif form.validate_on_submit():
            if not check_distinct_clubhouse_usernames(request.form['username']):
                flash(_l("This username is already taken."))
            else:
                message, new_club_id = add_clubhouse(convert_form_to_dict(request.form, ["add_btn","confirm", "csrf_token"]))
#                flash(_l(add_clubhouse(convert_form_to_dict(request.form, ["add_btn", "confirm", "csrf_token"]))))
                flash(message)
                session['edit_club_id'] = new_club_id
                return redirect('/admin/editclubhouse')
    return render_template('/admin/add.html', form=form)
