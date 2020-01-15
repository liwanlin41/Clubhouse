# login form and checkin form

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l
from helpers import binary_search
from .db import *

class LoginForm(FlaskForm):
    user = StringField(_l('Username'), validators = [DataRequired()])
    password = StringField(_l('Password'), validators = [DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class CheckinForm(FlaskForm):
    '''create the checkin form template, not specialized for any data'''
    # key members by id for form submission
    members_in = []
    members_out = []
    # field for members to check in
    check_in_id = SelectField(_l("Member List"), choices = members_out)
    # field for checked-in members to check out
    check_out_id = SelectField(_l("Members Currently in Clubhouse"), choices = members_in)
    check_in = SubmitField(_l('Check In'))
    check_out = SubmitField(_l('Check Out'))

# handle all check in/out operations
class CheckinManager:
    def __init__(self, clubhouse=None):
        self.check_in_form = CheckinForm()
        if clubhouse:
            self.clubhouse = clubhouse # clubhouse is id number
            # get list of all members and key by member id
            self.id_to_name = {}
            for mem_id, first, last in get_clubhouse_members(self.clubhouse):
                self.id_to_name[(mem_id)] = first + " " + last
            # TODO: load actual check in/out lists from database
            # make all members signed out for testing purposes
            self.members_out = [(num, self.id_to_name[num]) for num in self.id_to_name]
            self.members_out.sort(key = lambda x: x[1])
            self.members_in = []
        if not clubhouse: # testing purposes
            # NOTE: translation not needed here because names are displayed
            self.members_in = [(123,"manager signed-in 1"), (234,"manager signed-in 2")]
            self.members_out = [(12,"manager signed-out 3"),(23,"manager signed-out 4")]
            # dictionary linking member id to member name
            self.id_to_name = {
                    123: "manager signed-in 1",
                    234: "manager signed-in 2",
                    12: "manager signed-out 3",
                    23: "manager signed-out 4"}
        self.setfields()

    # reset the SelectField choices
    def setfields(self):
        self.check_in_form.check_in_id.choices = self.members_out
        self.check_in_form.check_out_id.choices = self.members_in

    # check in member id_num
    # move from out list to in list
    def checkin_member(self, id_num):
        # extract member to be removed
        member = (id_num, self.id_to_name[id_num])
        self.members_out.remove(member)
        # check-in to database
        # TODO: check syntax
        add_checkin()
        # insert member into sorted members_in list
        self.members_in.insert(binary_search(self.members_in, self.id_to_name[id_num]), member)
        self.setfields() # update visual

    # check out member id_num
    # move from in list to out list
    def checkout_member(self, id_num):
        # extract member to be removed
        member = (id_num, self.id_to_name[id_num])
        self.members_in.remove(member)
        add_checkout()
        self.members_out.insert(binary_search(self.members_out, self.id_to_name[id_num]), member)
        self.setfields()
