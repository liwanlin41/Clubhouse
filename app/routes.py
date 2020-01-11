# handle all routing things

# not sure what the imports should be but these seem to work?
from flask import render_template, flash, redirect, request
from app import app
from app.forms import LoginForm

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
