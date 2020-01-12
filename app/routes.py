# handle all routing things

# not sure what the imports should be but these seem to work?
from flask import render_template, flash, redirect, request
from app import app
from app.forms import LoginForm
from flask_babel import lazy_gettext as _l

### homepages

@app.route('/')
def home():
#    return "Hello"
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
        return redirect('admin')
    return render_template('login.html', form=form)

