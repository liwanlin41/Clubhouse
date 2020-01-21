# helper functions for database operations, all functions with db accesses should be here

from datetime import datetime
from app import conn
from werkzeug.security import generate_password_hash

# retrieve cursor for MySQL database defined in env vars
def get_cursor():
    cursor = conn.cursor()
    return cursor

# retrieve members from a clubhouse: returns (id, first, last)
def get_clubhouse_members(clubhouse_id, sort_by_last=True):
    cursor = get_cursor()
    sorting = "first_name, last_name" # can collapse if statement to one line
    if sort_by_last:
        sorting = "last_name, first_name"
    # temporarily hard-coded sort order
    cursor.execute("SELECT member_id, first_name, last_name FROM members WHERE clubhouse_id = %s ORDER BY last_name, first_name", (clubhouse_id,))
    rows = cursor.fetchall()
#    for row in rows: # for debugging purposes?
#        print(row)
    cursor.close()
    return rows

# retrieve a specific member: returns the whole row by default
def get_specific_member(clubhouse_id, member_id, short_form=False):
    cursor = get_cursor()
    if short_form:      # return (first, last) only
        cursor.execute("""SELECT first_name, last_name
                          FROM members
                          WHERE clubhouse_id = %s
                          AND member_id = %s""", (clubhouse_id, member_id))
    else:
        cursor.execute("SELECT * FROM members WHERE clubhouse_id = %s AND member_id = %s", (clubhouse_id, member_id))
    member = cursor.fetchall()
    if len(member) > 1: # error statements don't actually work lol
        app.logger.error("error: found more than two members with these ids") # shouldn't happen
    if len(member) < 1:
        app.logger.error("error: didn't find anyone with these ids")
    cursor.close()
    app.logger.info("get specific member debug: ", member)
    return member[0]

# retrieve a list of members that are currently checked into a clubhouse: returns (id, (first, last))
def get_checked_in_members(clubhouse_id, sort_by_last=True):
    current_time = datetime.now()

    sorting = "first_name, last_name" # can collapse if statement to one line
    if sort_by_last:
        sorting = "last_name, first_name"
    cursor = get_cursor()
    cursor.execute("""SELECT member_id, clubhouse_id FROM checkins
                      WHERE clubhouse_id = %s
                      AND checkin_datetime < %s
                      AND checkout_datetime IS NULL""", (clubhouse_id, current_time))
    members = cursor.fetchall()

    result = []
    for (member_id, clubhouse_id) in members:
        # TODO: sort result by sort_by_last
        result.append((member_id,get_specific_member(clubhouse_id, member_id, True)))
    cursor.close()
    return result

# retrieve only certain members (for filtering)
def query_members():
    pass

# register a new member
def add_member():
    cursor = get_cursor()
    cursor.execute("""INSERT INTO members (first_name, last_name, clubhouse_id)
                    VALUES ('carolyn', 'mei', 1)""")
    conn.commit()
    cursor.close()

# delete a specific member
def delete_specific_member(club_id, mem_id):
    cursor = get_cursor()
    # delete from members table
    cursor.execute("""DELETE FROM members
                        WHERE clubhouse_id = %s
                        AND member_id = %s""",
                        (club_id, mem_id))
    # delete from checkins table
    # temporary patch to ensure user does not appear in checked-in users
    current_time = datetime.now()
    cursor.execute("""UPDATE checkins
                      SET checkout_datetime = %s
                      WHERE member_id = %s
                      AND clubhouse_id = %s
                      AND checkout_datetime IS NULL""",
                      (current_time, mem_id, club_id))
#    cursor.execute("""DELETE FROM checkins
#                        WHERE clubhouse_id = %s
#                        AND member_id = %s""",
#                        (club_id, mem_id))
    conn.commit()
    cursor.close()
    return "Member deleted successfully." # could be more specific but that requires getting more info

# retrieve all check-ins
def get_all_checkins():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM checkins")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# retrieve only certain check-ins (for filtering)
def query_checkins():
    pass

# add a new check-in
def add_checkin(member_id, clubhouse_id):
    current_time = datetime.now()
    cursor = get_cursor()
    # for testing, change later
    cursor.execute("""INSERT INTO checkins (member_id, checkin_datetime, clubhouse_id)
                      VALUES (%s, %s, %s)""",
                      (member_id, current_time, clubhouse_id))
    conn.commit()
    cursor.close()

# add a new check-out, edits checkins table
def add_checkout(member_id, clubhouse_id):
    current_time = datetime.now()
    cursor = get_cursor()
    # for testing, change later
    cursor.execute("""UPDATE checkins
                      SET checkout_datetime = %s
                      WHERE member_id = %s
                      AND clubhouse_id = %s
                      AND checkout_datetime IS NULL""",
                      (current_time, member_id, clubhouse_id))
    conn.commit()
    cursor.close()

# get login information
# on an attempted login with username username,
# retrieve the user id from table
# return id or None if username is invalid
# can we give the admin a special id that doesn't clash with clubhouses?
def get_id_from_username(username):
    # for testing
    if username == "hi":
        return 1
    elif username == "admin":
        return 2
    else:
        return None

# given id number of user, retrieve user info or tuple of None
def get_user_from_id(id_num):
    # for testing
    if id_num == 1:
        return (1, "hi", generate_password_hash("test"))
    elif id_num == 2:
        return (2, "admin", generate_password_hash("admin"))
    return (None, None, None)
