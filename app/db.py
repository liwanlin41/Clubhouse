# helper functions for database operations, all functions with db accesses should be here

from datetime import datetime
from app import app, conn
from werkzeug.security import generate_password_hash
from flask_babel import lazy_gettext as _l

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

# returns True if the member is currently checked in, False otherwise
def is_checked_in(clubhouse_id, member_id):
    cursor = get_cursor()
    cursor.execute("""SELECT is_checked_in
                      FROM members
                      WHERE clubhouse_id = %s
                      AND member_id = %s""", (clubhouse_id, member_id))
    member = cursor.fetchall()
    if len(member) > 1: # error statements don't actually work lol
        app.logger.error("error: found more than two members with these ids") # shouldn't happen
    if len(member) < 1:
        app.logger.error("error: didn't find anyone with these ids")
    cursor.close()
    return member[0][0]

# retrieve a list of members that are currently checked into a clubhouse: returns (id, (first, last))
def get_checked_in_members(clubhouse_id, sort_by_last=True):
    members = get_clubhouse_members(clubhouse_id, sort_by_last)

    result = []
    for (member_id, first, last) in members:
        if is_checked_in(clubhouse_id, member_id):
            result.append((member_id, (first, last)))
    return result

# retrieve only certain members (for filtering)
def query_members():
    pass

# register a new member, starts checked out by default
def add_member(club_id, update_dict):
    cursor = get_cursor()
    # insert blank row with just member_id
    cursor.execute("""INSERT INTO members (member_id, first_name, last_name, clubhouse_id)
                        VALUES (DEFAULT, 'temp_first', 'temp_last', %s)""",
                        (club_id))

    # get this id that we just created (LAST_INSERT_ID() apparently not supported w/ our v of MySQL?)
    cursor.execute("""SELECT LAST_INSERT_ID()""")
    member_ids = cursor.fetchall()
    if len(member_ids) != 1:
        app.logger.error("There should only be one ID.")
        app.logger.error(member_ids)
    new_member_id = member_ids[0]

    # update each field separately
    for key in update_dict:
        query = """UPDATE members
                    SET %s = %%s
                    WHERE clubhouse_id = %%s
                    AND member_id = %%s""" % key
        cursor.execute(query, (update_dict[key], club_id, new_member_id))

    conn.commit()
    cursor.close()
    return _l("Member added successfully.") # again could be more specific

# edit a member
def edit_member(club_id, mem_id, update_dict):
    cursor = get_cursor()
    for key in update_dict: # key has to match exact vocabulary of table
        query = """UPDATE members
                   SET %s = %%s
                   WHERE clubhouse_id = %%s
                   AND member_id = %%s""" % key
        cursor.execute(query, (update_dict[key], club_id, mem_id))

    conn.commit()
    cursor.close()
    return _l("Member updated successfully.") # could be more specific but that requires getting more info

# delete a specific member
def delete_specific_member(club_id, mem_id):
    cursor = get_cursor()
    # delete from members table
    cursor.execute("""DELETE FROM members
                        WHERE clubhouse_id = %s
                        AND member_id = %s""",
                        (club_id, mem_id))
    # delete from checkins table
    # temporary patch to ensure user does not appear in checked-in users -- where did attempted actual sol'tn go?
    current_time = datetime.now()
    cursor.execute("""UPDATE checkins
                      SET checkout_datetime = %s
                      WHERE member_id = %s
                      AND clubhouse_id = %s
                      AND checkout_datetime IS NULL""",
                      (current_time, mem_id, club_id))
    conn.commit()
    cursor.close()
    return _l("Member deleted successfully.") # could be more specific but that requires getting more info

# retrieve all check-ins
def get_all_checkins():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM checkins")
    rows = cursor.fetchall()
    cursor.close()
    return rows

# retrieve only check-ins from a certain clubhouse
def get_checkins_by_clubhouse(clubhouse_id):
    cursor = get_cursor()
    cursor.execute("""SELECT * FROM checkins
                      WHERE clubhouse_id = %s""", (clubhouse_id, ))
    rows = cursor.fetchall()
    cursor.close()
    return rows

# changes the is_checked_in field for a given member
def change_member_checkin(member_id, clubhouse_id, checked_in):
    cursor = get_cursor()
    cursor.execute("""UPDATE members
                      SET is_checked_in = %s
                      WHERE clubhouse_id = %s
                      AND member_id = %s""", (checked_in, clubhouse_id, member_id))
    conn.commit()
    cursor.close()
    return "Check-in status changed successfully."

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
    change_member_checkin(member_id, clubhouse_id, True)

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
    change_member_checkin(member_id, clubhouse_id, False)

### admin side ###

# given id number of clubhouse, get clubhouse name (either 'short_name' or 'full_name')
# mostly copied from get_specific_member
def get_clubhouse_from_id(club_id, name="short_name"):
    cursor = get_cursor()
    query = """SELECT %s FROM clubhouses WHERE clubhouse_id = %%s""" % name
    cursor.execute(query, (club_id,))
    club_name = cursor.fetchall()
    conn.commit()
    cursor.close()
    if len(club_name) > 1:
        app.logger.error("error: found more than two clubhouses with these ids")
    elif len(club_name) < 1:
        app.logger.error("error: didn't find any clubhouse with this id")
    return club_name[0][0]

# analog to get_clubhouse_members, return id,name (either short or long name)
# ordered alphabetically
def get_all_clubhouses(name="short_name"):
    cursor = get_cursor()
    cursor.execute("""SELECT clubhouse_id, %s FROM clubhouses
                        ORDER BY %s""" % (name, name))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    return rows

# check to make sure usernames are distinct
def check_distinct_clubhouse_usernames(proposed_username):
    cursor = get_cursor()

    cursor.execute("""SELECT username FROM logins 
                        WHERE username = %s
                        AND is_admin = 0""",
                        (proposed_username))
    repeats = cursor.fetchall()
    if len(repeats) > 0:
        # another clubhouse already has this nickname
        return False
    return True

# adds and creates a clubhouse, similar to add_member
def add_clubhouse(update_dict):
    cursor = get_cursor()

    # create clubhouse row
    cursor.execute("""INSERT INTO clubhouses (clubhouse_id, short_name, full_name)
                        VALUES (DEFAULT, 'NULL', 'temp_full')""") # may error if other values have no default

    # get this id that we just created 
    cursor.execute("""SELECT LAST_INSERT_ID()""")
    club_ids = cursor.fetchall()
    if len(club_ids) != 1:
        app.logger.error("There should only be one ID.")
        app.logger.error(club_ids)
    new_club_id = club_ids[0]

    # create login row
    cursor.execute("""INSERT INTO logins (user_id, username, password, clubhouse_id, is_admin)
                        VALUES (DEFAULT, %s, %s, %s, DEFAULT)""",
                        (update_dict['username'], update_dict['password'], new_club_id))
    # TODO: eventually switch to the bottom which stores the password hash instead of password
#                        (update_dict['username'], generate_password_hash(update_dict['password']), new_club_id))

    # update each field separately
    for key in update_dict:
        # logins already done
        if key == "username" or key == "password":
            pass
        # update clubhouse fields
        else:
            query = """UPDATE clubhouses
                        SET %s = %%s
                        WHERE clubhouse_id = %%s""" % key
            cursor.execute(query, (update_dict[key], new_club_id))
    conn.commit()
    cursor.close()
    return _l("Clubhouse added successfully.") # again could be more specific

def delete_clubhouse(club_id):
    cursor = get_cursor()
    # delete clubhouse row
    cursor.execute("""DELETE FROM clubhouses
                        WHERE clubhouse_id = %s""",
                        (club_id))
    # delete clubhouse login row
    cursor.execute("""DELETE FROM logins
                        WHERE clubhouse_id = %s""",
                        (club_id))

    # TODO: if requested, delete all members in this clubhouse and all their checkins

    conn.commit()
    cursor.close()
    return _l("Clubhouse removed successfully.")

# get login information
# on an attempted login with username username,
# retrieve the user id from table
# return user id or None if username is invalid
def get_id_from_username(username):
    cursor = get_cursor()
    cursor.execute("""SELECT user_id FROM logins
                    WHERE username = %s""", (username,))
    users = cursor.fetchall()
    cursor.close()
    if len(users) == 0: # no such user
        return None
    if len(users) > 1:
        # TODO: force unique usernames
        app.logger.error("Multiple users with this username")
    else:
        return users[0][0]

# given either the username or the id of a clubhouse account
# return club id for that account
# TODO: implement
def get_club_id_from_user(user_id = None, username = None):
    if user_id:
        cursor = get_cursor()
        cursor.execute("""SELECT clubhouse_id FROM logins
                    WHERE user_id = %s""", (user_id,))
        club_ids = cursor.fetchall()
        cursor.close()
        if len(club_ids) != 1:
            app.logger.error("There should be exactly one clubhouse with this user id")
        else:
            return club_ids[0][0]
    elif username: # get from username
        if username == "hi":
            return 1
        elif username == "admin":
            return 2
        else:
            return None

# given id of clubhouse, get the corresponding user id
def get_user_id_from_club(club_id):
    cursor = get_cursor()
    cursor.execute("""SELECT user_id FROM logins
                    WHERE clubhouse_id = %s""", (club_id,))
    user_ids = cursor.fetchall()
    cursor.close()
    if len(user_ids) != 1:
        app.logger.error("Only one clubhouse should have this id.")
    else:
        return user_ids[0][0]

# given id number of user, retrieve user info or tuple of None
# if last_name is True, members will be listed by last name
# return (id, username, password hash, club_id, is_admin, last_name)
# here id is the user login id
def get_user_from_id(id_num):
    cursor = get_cursor()
    cursor.execute("""SELECT * FROM logins
                    WHERE user_id = %s""", (id_num,))
    users = cursor.fetchall()
    if len(users) != 1:
        app.logger.error("There should be exactly one user with this user id.")
    else:
        # TODO: add last_name field and password hash so this is just a return
        u_id, username, password, club_id, is_admin = users[0]
        return (u_id, username, generate_password_hash(password), club_id, is_admin, False)
    # for testing
#    if id_num == 1:
#        return (1, "hi", generate_password_hash("test"), False, True)
#    elif id_num == 2:
#        return (2, "admin", generate_password_hash("admin"), True, False)
    return (None, None, None, None, None, None)

# HELPER FUNCTION: also removes empty fields
def convert_form_to_dict(form, to_remove):
    # convert to mutable dictionary
    update_dict = dict(form) # WARNING: values are in list form
    # remove all empty/unnecessary fields
    for key in update_dict:
        if type(update_dict[key]) == list and len(update_dict[key]) == 1:
            update_dict[key] = update_dict[key][0]
    for field in update_dict:
        if len(update_dict[field]) == 0:
            to_remove.append(field)
    for field in to_remove:
        del update_dict[field]
    return update_dict

#TODO: implement
# set password of user id_num to password
# update last_name field to last_name
# id_num is user id
def update_password(id_num, password, last_name):
    print((id_num, password, last_name))
