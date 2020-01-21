# initialization file, a bunch of imports and stuff

import os
from flask import Flask, request
from config import Config
from flask_babel import Babel, _
from flask_login import LoginManager
from flaskext.mysql import MySQL

# initialize configuration
app = Flask(__name__)
app.config.from_object(Config)

# set up database access
app.config.update(
    MYSQL_DATABASE_USER = os.getenv('MYSQL_DATABASE_USER', 'root'),
    MYSQL_DATABASE_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD', 'root'),
    MYSQL_DATABASE_DB = os.getenv('MYSQL_DATABASE_DB', 'clubhouse'),
    MYSQL_DATABASE_HOST = os.getenv('MYSQL_DATABASE_HOST', 'localhost'),
    MYSQL_DATABASE_SOCKET = None
)
mysql = MySQL()
mysql.init_app(app)
conn = mysql.connect()

# multi-language support
babel = Babel(app)
@babel.localeselector
def get_locale():
#    return 'es'
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# these things don't work yet, person working on these parts can do whatever necessary

# login setup
login_manager = LoginManager(app)
login_manager.login_view = 'login'
login_manager.refresh_view = 'reauthenticate'
app.fresh = True # set session as fresh to avoid errors later
# TODO: localize messages

# this import needs to come at the end, don't touch; later the other imported files will also be here
from app import db
from app import routes
from app import models
