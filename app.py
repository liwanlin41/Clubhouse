from flask import Flask, render_template
app = Flask(__name__)

@app.route('/')
def home():
    return render_template('index.html')
#    return "home page"

@app.route('/clubhouse')
def club_home():
    return render_template('/clubhouse/home.html')
