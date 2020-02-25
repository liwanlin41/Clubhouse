# initialization file, a bunch of imports and stuff

import os
from flask import Flask, request
from config import Config
from flask_babel import Babel, _
from flask_babel import lazy_gettext as _l
from flask_login import LoginManager
from flaskext.mysql import MySQL

# initialize configuration
application = Flask(__name__)
application.config.from_object(Config)

# set up database access
application.config.update(
    MYSQL_DATABASE_USER = os.getenv('MYSQL_DATABASE_USER', 'root'),
    MYSQL_DATABASE_PASSWORD = os.getenv('MYSQL_DATABASE_PASSWORD', 'root'),
    MYSQL_DATABASE_DB = os.getenv('MYSQL_DATABASE_DB', 'clubhouse'),
    MYSQL_DATABASE_HOST = os.getenv('MYSQL_DATABASE_HOST', 'localhost'),
    MYSQL_DATABASE_SOCKET = None
)
mysql = MySQL()
mysql.init_app(application)
conn = mysql.connect()

# multi-language support
babel = Babel(application)
@babel.localeselector
def get_locale():
#    return 'es'
    return request.accept_languages.best_match(application.config['LANGUAGES'])

# login setup
login_manager = LoginManager(application)
login_manager.login_view = 'login'
login_manager.refresh_view = 'reauthenticate'
login_manager.login_message = _l("Please log in to access this page.")
login_manager.needs_refresh_message = _l("Please reauthenticate to view this page.")

# this import needs to come at the end, don't touch; later the other imported files will also be here
from application import db
from application import routes
from application import models
