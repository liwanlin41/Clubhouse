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
            # TODO: actually set this field
            self.display_last = False # whether to display last name first
            # get list of all members and key by member id
            self.id_to_name = {}
            self.members_out = []
            for mem_id, first, last in get_clubhouse_members(self.clubhouse):
                # separate first and last names for sorting purposes
                self.id_to_name[(mem_id)] = (first, last)
                # list is already sorted, initialize members_out here
                self.members_out.append(self.get_member_display(mem_id))
            # TODO: load actual check in/out lists from database
            # check syntax on later updates
            self.members_in = []
            # parse checked-in members and remove them from checked-out list
            for mem_id, club_id, in_time, out_time in get_all_checkins():
                if out_time:
                    member = self.get_member_display(mem_id)
                    self.members_in.append(member)
                    self.members_out.remove(member)
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

    # return (id_num, first last) or (id_num, last first)
    def get_member_display(self, id_num):
        first, last = self.id_to_name[id_num]
        if self.display_last:
            return (id_num, last + ", " + first)
        return (id_num, first + " " + last)

    # check in member id_num
    # move from out list to in list
    def checkin_member(self, id_num):
        # extract member to be removed
        member = self.get_member_display(id_num)
        self.members_out.remove(member)
        # check-in to database
        # TODO: check syntax
        add_checkin()
        # insert member into sorted members_in list
        # x[0] gets member id, the rest gets last, first for sorting order
        self.members_in.insert(binary_search(self.members_in, member, key = lambda x: self.id_to_name[x[0]][1] + ", " + self.id_to_name[x[0]][0]), member)
#        self.members_in.insert(binary_search(self.members_in, self.id_to_name[id_num], key = lambda x: x[1]), member)
        self.setfields() # update visual

    # check out member id_num
    # move from in list to out list
    def checkout_member(self, id_num):
        # extract member to be removed
        member = self.get_member_display(id_num)
        self.members_in.remove(member)
        add_checkout()
        self.members_out.insert(binary_search(self.members_out, member, key = lambda x: self.id_to_name[x[0]][1] + ", " + self.id_to_name[x[0]][0]), member)
#       self.members_out.insert(binary_search(self.members_out, self.id_to_name[id_num], key = lambda x: x[1]), member)
        self.setfields()
