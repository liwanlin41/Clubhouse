# helper functions for database operations, all functions with db accesses should be here

from flaskext.mysql import MySQL
from app import app

# retrieve cursor for MySQL database defined in env vars
def get_cursor():
    mysql = MySQL()
    mysql.init_app(app)
    cursor = mysql.get_db().cursor()

# retrieve all members
def get_all_members():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM TABLE member_info")
    rows = cursor.fetchall()
    return rows

# retrieve only certain members (for filtering)
def query_members():
    pass

# register a new member
def add_member():
    cursor = get_cursor()
    # for testing, change later
    cursor.execute("INSERT INTO TABLE member_info (first_name, last_name) VALUES (carolyn, mei)")

# retrieve all check-ins
def get_all_checkins():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM TABLE member_info")
    rows = cursor.fetchall()
    return rows

# retrieve only certain check-ins (for filtering)
def query_checkins():
    pass

# add a new check-in
def add_checkin():
    pass

# add a new check-out, edits checkins table
def add_checkout():
    pass
