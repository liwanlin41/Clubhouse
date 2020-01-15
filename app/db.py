# helper functions for database operations, all functions with db accesses should be here

from flaskext.mysql import MySQL
from app import app

# retrieve cursor for MySQL database defined in env vars
def get_cursor():
    mysql = MySQL()
    mysql.init_app(app)
    cursor = mysql.get_db().cursor()

# retrieve members from a clubhouse: returns (id, first, last)
def get_clubhouse_members(clubhouse_id, sort_by_last=True):
    cursor = get_cursor()
    sorting = "first_name, last_name" # can collapse if statement to one line
    if sort_by_last:
        sorting = "last_name, first_name"
    cursor.execute("SELECT member_id, first_name, last_name FROM TABLE member_info WHERE clubhouse_id = ? ORDER BY ?"; (clubhouse_id, sorting))
        # ^ may be sketch in terms of ordering and the ? variable thing (a matter of security)
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
