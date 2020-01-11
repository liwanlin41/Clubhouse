# initialization file, a bunch of imports and stuff

from flask import Flask, request
from config import Config
from flask_babel import Babel, _
#from flask_login import LoginManager
#from flaskext.mysql import MySQL

# initialize configuration
app = Flask(__name__)
app.config.from_object(Config)

# multi-language support
babel = Babel(app)
@babel.localeselector
def get_locale():
#    return 'es'
    return request.accept_languages.best_match(app.config['LANGUAGES'])

# these things don't work yet, person working on these parts can do whatever necessary

# login setup
#db = MySQL(app) # database
#database_name = "database.db"
#cur = db.connector.cursor()
#cur.execute("CREATE TABLE IF NOT EXISTS coord_info ( username VARCHAR(10), password_hash VARCHAR(30), email VARCHAR(30));")

#login_manager = LoginManager()
#login_manager.init_app(app)

# this import needs to come at the end, don't touch; later the other imported files will also be here
from app import routes
