# handle all routing things

# not sure what the imports should be but these seem to work?
from functools import wraps
from flask import render_template, flash, redirect, request, url_for
from app import app
from app.forms import LoginForm, CheckinManager, MemberManager, MemberAddForm, MemberInfoHandler, AuthenticateForm
from flask_babel import lazy_gettext as _l
from flask_login import current_user, login_user, logout_user
from .db import *
from .plot import *
from .models import *

# function for two-level authentication
def login_required(access="basic"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated: # user not logged in
                return login_manager.unauthorized()
            # access is either basic or admin
            if current_user.access != access and access != "basic":
                flash(_l("Insufficient credentials."))
                return redirect('/')
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

def fresh_login_required(access="basic"):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            if not current_user.is_authenticated:
                return login_manager.unauthorized()
            elif current_user.access != access and access !="basic":
                flash(_l("Insufficient credentials."))
                return redirect('/')
            elif not app.fresh:
                return login_manager.needs_refresh()
            return fn(*args, **kwargs)
        return decorated_view
    return wrapper

### homepages

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clubhouse')
@fresh_login_required()
def club_home():
    if current_user.access == "admin":
        # TODO: implement this
        return("please choose a clubhouse to view")
    return render_template('/clubhouse/home.html')

@app.route('/admin')
@fresh_login_required(access="admin")
def admin_home():
    return render_template('/admin/home.html')

# view data pages
@app.route('/clubhouse/view', methods=['GET','POST'])
@fresh_login_required()
def coord_view():
    # the time_range will return the number of days to be considered
    # [1, 7, 30, 365] corresponding to day, week, month, year
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    # TODO: name things better, come up with a better indexing system?
    # 0 is meant to be raw data, e.g. number of people on each day
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week"))]
    if request.method == 'POST':
        # TODO: title the graph and update to getting checkins for a given clubhouse
        # extract relevant information
        cur_range = request.form['range']
        cur_format = request.form['format']
        # pass cur_range, cur_format to template 
        # to keep them displayed on the page (minimize confusion)
        return render_template('/clubhouse/view.html', time_ranges=time_ranges, data_format=data_format, plot=plot(cur_range, cur_format), cur_range =int(cur_range), cur_format = int(cur_format))
    if request.method == 'GET':
        # default cur_range, cur_format to be the first in the list
        return render_template('/clubhouse/view.html', time_ranges=time_ranges, data_format=data_format, cur_range = time_ranges[0][0], cur_format = data_format[0][0])

@app.route('/admin/view', methods=['GET', 'POST'])
@fresh_login_required(access="admin")
def admin_view():
    # copied from coord_view
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week"))]
    if request.method == 'POST':
        #TODO: actually pull data
        return "this method has not been implemented"
    if request.method == 'GET':
        return render_template('/admin/view.html', time_ranges=time_ranges, data_format=data_format)

# logins and logouts

# logout routing
@app.route('/logout')
def logout():
    logout_user()
    return redirect('/')

# basic login form, it doesn't post anything yet
@app.route('/login', methods=['GET','POST'])
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
        club_id = get_id_from_username(username)
        if club_id: # valid user
            user = User(club_id) # generate user object
            if user.check_password(password): # login success
                login_user(user, remember=form.remember.data)
                app.fresh = True # manually set fresh session
                # redirect based on user status
                if user.access == "admin":
                    return redirect('/admin')
                return redirect('/clubhouse')
        # display that credentials are incorrecrt
        flash(_l("Username/password combination incorrect."))
        return redirect('/login')
    return render_template('login.html', form=form, refresh = False)

# page for reauthentication
@app.route('/reauthenticate', methods=['GET','POST'])
@login_required()
def reauthenticate():
    form = AuthenticateForm()
    if form.validate_on_submit():
        # read user input to form
        password = request.form['password']
        if current_user.check_password(password): # login success
            app.fresh = True # session is now fresh
            # redirect based on user status
            if current_user.access == "admin":
                return redirect('/admin')
            return redirect('/clubhouse')
        # display that credentials are incorrecrt
        flash(_l("Incorrect password."))
        return redirect('/reauthenticate')
    return render_template('login.html', form=form, refresh = True)


# this is no longer needed, one login handles everything
# same as above, only for admins
#@app.route('/admin/login', methods=['GET','POST'])
#def admin_login():
#    form = LoginForm()
#    if form.validate_on_submit():
#        raw_data = request.form
#        return redirect('/admin')
#    return render_template('login.html', form=form)

# rest of app routes for clubhouse home page

# add new member
@app.route('/clubhouse/addmember', methods=['GET','POST']) # might need a method -- better to make html name informative if different?
@fresh_login_required()
def create_member():
    form = MemberAddForm()
    if request.method == 'POST':
        if "cancel_btn" in request.form:
            return redirect('/clubhouse/members')
        elif form.validate_on_submit():
        # TODO: add member info to database
            add_member()
            return request.form
    return render_template('/clubhouse/edit.html', form=form, new_member=True)

@app.route('/clubhouse/members', methods=['GET','POST'])
@fresh_login_required()
def manage_members():
    club_id = 1 # TODO: get actual clubhouse id
    form_manager = MemberManager(club_id)
    if request.method == "POST":
        if "new_member" in request.form: # add new member
            return redirect('/clubhouse/addmember')
        # view or edit button pressed but no member selected
        if "memberselect" not in request.form: # this is invalid
            return redirect('/clubhouse/members')
        member_id = int(request.form['memberselect'])
        if "edit" in request.form: # everything else should fall here
            handle = MemberInfoHandler(get_specific_member(club_id, member_id))
            # go to form to edit member information
            # NOTE: there may be errors with form resubmission and back button handling here
            return render_template('/clubhouse/edit.html',form=handle.form, new_member=False)
    return render_template('/clubhouse/membership.html', form=form_manager.member_form)

@app.route('/clubhouse/editmember',methods=['POST'])
@fresh_login_required()
def edit_member():
    if request.method == 'POST':
        if "cancel_btn" in request.form: # cancel the updates
            return redirect('/clubhouse/members')
        club_id = int(request.form['club_id'])
        mem_id = int(request.form['mem_id'])
        if "delete_btn1" in request.form: # first click of delete button
            # go to confirmation step
            flash(_l("WARNING: Attempting to delete member - this action is irreversible. Click 'Remove Member' again to confirm."))
            # display message and require resubmit
            # note this will also clear all fields
            # TODO: store data if remove is clicked but then canceled?
            # alternatively just find a better confirmation solution
            handle = MemberInfoHandler(get_specific_member(club_id, mem_id))
            return render_template('/clubhouse/edit.html',form=handle.form, new_member=False, second_del = True)
        if "delete_btn2" in request.form: # delete member from active members
            flash(_l(delete_specific_member(club_id, mem_id))) # delete from db, returns success/error message
            return redirect('/clubhouse/members')
        # otherwise update info
        # TODO: update member info in database
        if "update_btn" in request.form:
            # oop no time
        # this post request contains the member id and club id
        return request.form

# TODO: remove this route
@app.route('/clubhouse/viewmembers')
def view_members():
    return str(get_clubhouse_members(1))

# check-in page, main functionality of website
@app.route('/clubhouse/checkin', methods=['GET','POST'])
@login_required()
def checkin_handler():
    # manually set session to stale
    app.fresh = False
    if request.method == "GET":
        # TODO: this is currently a test clubhouse id
        # will need to get the actual clubhouse id eventually
        app.testform = CheckinManager(1) # persistence
    if request.method == "POST":
        # TODO: find a better solution to form resubmission error
        try:
            if "check_in" in request.form and "check_in_id" in request.form: # check-in button clicked
                app.testform.checkin_member(int(request.form["check_in_id"]))
            elif "check_out_id" in request.form: # check-out button
                app.testform.checkout_member(int(request.form["check_out_id"]))
            return render_template('/clubhouse/checkin.html',form=app.testform.check_in_form)
        except ValueError: # cheating way to handle form resubmission
            return redirect('/clubhouse/checkin')
    return render_template('/clubhouse/checkin.html',form=app.testform.check_in_form)


# rest of app routes for admin home page (aka just editclubhouses)
@app.route('/admin/editclubhouses')
@fresh_login_required(access="admin")
def admin_clubhouses():
    return render_template('/admin/add.html')
