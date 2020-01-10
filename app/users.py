# none of this works
# this file should handle user login information and user accounts, etc.

from datetime import datetime
from app import admin_db, coord_db
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin

class admin():
    user_id = admin_db.Column(admin_db.Integer, primary_key=True)
    username = admin_db.Column(admin_db.String(64), index=True, unique=True)
    email = admin_db.Column(admin_db.String(120), index = True, unique=True)
    password_hash = admin_db.Column(admin_db.String(128))

#class checkin(UserMixin, db.Model):
#    timestamp = db.Column(db.DateTime, index = True, default=datetime.utcnow)
