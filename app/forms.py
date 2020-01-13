# login forms and other web forms

from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, BooleanField, SubmitField, SelectField
from wtforms.validators import DataRequired
from flask_babel import lazy_gettext as _l

class LoginForm(FlaskForm):
    user = StringField(_l('Username'), validators = [DataRequired()])
    password = StringField(_l('Password'), validators = [DataRequired()])
    remember = BooleanField(_l('Remember Me'))
    submit = SubmitField(_l('Sign In'))

class CheckinForm(FlaskForm):
    # SelectField is the one that has an entire box with all possible options
    # test data, TODO: replace with actual pulled data (pull either here or in routes.py when called)
    # key members by id for form submission
    members_in = [(123, _l("signed-in test member")), (12, _l("second signed-in test"))] # members currently in clubhouse
    members_out = [(234, _l("signed-out test member")), (345, _l("second signed-out test"))] # members not signed in
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
            self.clubhouse = clubhouse
            # TODO: load actual lists from database
        if not clubhouse:
            # NOTE: translation not needed here because names are displayed
            self.members_in = [("abc","manager signed-in 1"), ("bcd","manager signed-in 2")]
            self.members_out = [("ab","manager signed-out 3"),("bc","manager signed-out 4")]
            # dictionary linking member id to member name
            # ideally also load from database
            self.id_to_name = {
                    "abc": "manager signed-in 1",
                    "bcd": "manager signed-in 2",
                    "ab": "manager signed-out 3",
                    "bc": "manager signed-out 4"}
            self.setfields()

    # reset the SelectField choices
    # holy shit it works yayyyyyyyyy
    def setfields(self):
        self.check_in_form.check_in_id.choices = self.members_out
        self.check_in_form.check_out_id.choices = self.members_in

    # TODO: database update, either here or in routes.py

    # check in member id_num
    # move from out list to in list
    def checkin_member(self, id_num):
        # extract member to be removed
        member = (id_num, self.id_to_name[id_num])
        self.members_out.remove(member)
        # TODO: optimize for insertion into sorted list
        self.members_in.append(member)
        # sort member lists by displayed name
        self.members_in.sort(key = lambda x: x[1])
        self.setfields() # update visual

    # check out member id_num
    # move from in list to out list
    def checkout_member(self, id_num):
        # extract member to be removed
        member = (id_num, self.id_to_name[id_num])
        self.members_in.remove(member)
        # TODO: same as above
        self.members_out.append(member)
        self.members_out.sort(key = lambda x: x[1])
        self.setfields()
