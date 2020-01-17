# handle all routing things

# not sure what the imports should be but these seem to work?
from flask import render_template, flash, redirect, request, url_for
from app import app
from app.forms import LoginForm, CheckinManager, MemberManager, MemberAddForm, MemberInfoHandler
from flask_babel import lazy_gettext as _l
from .db import *

### homepages

@app.route('/')
def home():
    return render_template('index.html')

@app.route('/clubhouse')
def club_home():
    return render_template('/clubhouse/home.html')

@app.route('/admin')
def admin_home():
    return render_template('/admin/home.html')

# view data pages
@app.route('/clubhouse/view', methods=['GET','POST'])
def coord_view():
    # the time_range will return the number of days to be considered
    # [1, 7, 30, 365] corresponding to day, week, month, year
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    # TODO: name things better, come up with a better indexing system?
    # 0 is meant to be raw data, e.g. number of people on each day
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week"))]
    if request.method == 'POST':
        #TODO: actually pull data
        return "this method has not been implemented"
    if request.method == 'GET':
        return render_template('/clubhouse/view.html', time_ranges=time_ranges, data_format=data_format)

@app.route('/admin/view', methods=['GET', 'POST'])
def admin_view():
    # copied from coord_view
    time_ranges = [(1,_l("Last 24 hours")), (7,_l("Last 7 days")), (30,_l("Last month")), (365,_l("Last year"))]
    data_format = [(0, _l("Check-ins")), (1, _l("Time of day")), (2, _l("Day of week"))]
    if request.method == 'POST':
        #TODO: actually pull data
        return "this method has not been implemented"
    if request.method == 'GET':
        return render_template('/admin/view.html', time_ranges=time_ranges, data_format=data_format)

# basic login form, it doesn't post anything yet
@app.route('/clubhouse/login', methods=['GET','POST'])
def coord_login():
    form = LoginForm()
    if form.validate_on_submit():
        raw_data = request.form # read user input to form
        # TODO: check if username & password are valid
        return redirect('/clubhouse')
    return render_template('login.html', form=form)

# same as above, only for admins
@app.route('/admin/login', methods=['GET','POST'])
def admin_login():
    form = LoginForm()
    if form.validate_on_submit():
        raw_data = request.form
        return redirect('/admin')
    return render_template('login.html', form=form)

# rest of app routes for clubhouse home page

# add new member
@app.route('/clubhouse/addmember', methods=['GET','POST']) # might need a method -- better to make html name informative if different?
def create_member():
    if request.method == 'POST':
        # TODO: add member info to database
        return request.form
        if request.form["button"] == "Update":
            return("updating member")
        else: # new member
            add_member()
            return request.form
    # add_member()
    return render_template('/clubhouse/edit.html', form=MemberAddForm(), new_member=True)

@app.route('/clubhouse/members', methods=['GET','POST'])
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

@app.route('/clubhouse/editmember',methods=['GET','POST'])
def edit_member():
    if request.method == 'POST':
        # TODO: update member info in database
        return request.form

@app.route('/clubhouse/viewmembers')
def view_members():
    return str(get_clubhouse_members(1))

# check-in page, main functionality of website
@app.route('/clubhouse/checkin', methods=['GET','POST'])
def checkin_handler():
    # TODO: database connections
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
def admin_clubhouses():
    return render_template('/admin/add.html')
