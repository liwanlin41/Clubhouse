# handle all routing things

# not sure what the imports should be but these seem to work?
from flask import render_template, flash, redirect, request
from app import app
from app.forms import LoginForm

@app.route('/')
def home():
#    return "Hello"
    return render_template('index.html')

@app.route('/clubhouse')
def club_home():
    return render_template('/clubhouse/home.html')

# basic login form, I don't think it works yet
@app.route('/clubhouse/login', methods=['GET','POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        raw_data = request.form # read user input to form
        return redirect('/clubhouse')
    return render_template('login.html', form=form)
