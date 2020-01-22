# none of this works
# this file should handle user login information and user accounts, etc.

from datetime import datetime
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from .db import *
from app import login_manager

@login_manager.user_loader
def load_user(id_num):
    return User(int(id_num))

# user class, this is needed for compatibility with flask-login
class User(UserMixin):
    def __init__(self, id_num):
        super()
        # get user information
        num, username, password_hash, is_admin = get_user_from_id(id_num)
        if username: # valid id
            self.username = username
            self.id = id_num
            self.hash = password_hash
            # set user access level
            if is_admin:
                self.access = "admin"
                self.name = "Administrator"
                # setup impersonation info
                self.club_id = None
                self.impersonation = None
            else:
                self.access = "clubhouse"
                self.name = get_clubhouse_from_id(self.id)
            self.fresh = True # set as fresh session
        else: # I want to see if this ever happens
            raise ValueError

    def check_password(self, password):
        if check_password_hash(self.hash, password): # correct combo
            return True
        return False
