# helper functions for database operations, all functions with db accesses should be here

from datetime import datetime
#from application import application, conn
from application import application, mysql
from werkzeug.security import generate_password_hash
from flask_babel import lazy_gettext as _l

# retrieve connection for MySQL database defined in env vars
def get_conn():
    conn = mysql.connect()
#    cursor = conn.cursor()
    return conn

# retrieve members from a clubhouse: returns (id, first, last)
def get_clubhouse_members(clubhouse_id, sort_by_last=True):
    conn = get_conn()
    cursor = conn.cursor()
    sorting = "first_name, last_name" # can collapse if statement to one line
    if sort_by_last:
        sorting = "last_name, first_name"
    # temporarily hard-coded sort order
    cursor.execute("SELECT member_id, first_name, last_name FROM members WHERE clubhouse_id = %s AND active = 1 ORDER BY last_name, first_name", (clubhouse_id,))
    rows = cursor.fetchall()
#    for row in rows: # for debugging purposes?
#        print(row)
    cursor.close()
    conn.close()
    return rows

# retrieve member join dates: returns (id, join date)
def get_clubhouse_member_joindates(clubhouse_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, join_date FROM members WHERE clubhouse_id = %s AND active = 1 ORDER BY join_date", (clubhouse_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

def get_all_joindates():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT member_id, join_date FROM members WHERE active = 1 ORDER BY join_date")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# retrieve a specific member: returns the whole row by default
def get_specific_member(clubhouse_id, member_id, short_form=False):
    conn = get_conn()
    cursor = conn.cursor()
    if short_form:      # return (first, last) only
        cursor.execute("""SELECT first_name, last_name
                          FROM members
                          WHERE clubhouse_id = %s
                          AND member_id = %s""", (clubhouse_id, member_id))
    else:
        cursor.execute("SELECT * FROM members WHERE clubhouse_id = %s AND member_id = %s", (clubhouse_id, member_id))
    member = cursor.fetchall()
    if len(member) > 1: # error statements don't actually work lol
        application.logger.error("error: found more than two members with these ids") # shouldn't happen
    if len(member) < 1:
        application.logger.error("error: didn't find anyone with these ids")
    cursor.close()
    conn.close()
    application.logger.info("get specific member debug: ", member)
    return member[0]

# returns True if the member is currently checked in, False otherwise
def is_checked_in(clubhouse_id, member_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT is_checked_in
                      FROM members
                      WHERE clubhouse_id = %s
                      AND member_id = %s
                      AND active = %s""", (clubhouse_id, member_id, True))
    member = cursor.fetchall()
    if len(member) > 1: # error statements don't actually work lol
        application.logger.error("error: found more than two members with these ids") # shouldn't happen
    if len(member) < 1:
        application.logger.error("error: didn't find anyone with these ids")
    cursor.close()
    conn.close()
    return member[0][0]

# retrieve a list of members that are currently checked into a clubhouse: returns (id, (first, last))
def get_checked_in_members(clubhouse_id, sort_by_last=True):
    members = get_clubhouse_members(clubhouse_id, sort_by_last)

    result = []
    for (member_id, first, last) in members:
        if is_checked_in(clubhouse_id, member_id):
            result.append((member_id, (first, last)))
    return result

# same but for currently checked out: returns list of member_ids who have checked in but not out
    # may have to be called directly inside enable_auto_checkout
def get_checked_out_members(clubhouse_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT member_id FROM members
                        WHERE clubhouse_id = %s
                        AND active = 1
                        AND is_checked_in = 1""",
                        (clubhouse_id, ))
    checked_out = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return checked_out

# retrieve only certain members (for filtering)
def query_members():
    pass

# register a new member, starts checked out by default
# returns message, member id
def add_member(club_id, update_dict):
    conn = get_conn()
    cursor = conn.cursor()
    # insert blank row with just member_id
    cursor.execute("""INSERT INTO members (member_id, first_name, last_name, clubhouse_id)
                        VALUES (DEFAULT, 'temp_first', 'temp_last', %s)""",
                        (club_id, ))

    # get this id that we just created (LAST_INSERT_ID() apparently not supported w/ our v of MySQL?)
    cursor.execute("""SELECT LAST_INSERT_ID()""")
    member_ids = cursor.fetchall()
    if len(member_ids) != 1:
        application.logger.error("There should only be one ID.")
        application.logger.error(member_ids)
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
    conn.close()
    return (_l("Member added successfully."), new_member_id) # again could be more specific

# edit a member
def edit_member(club_id, mem_id, update_dict):
    conn = get_conn()
    cursor = conn.cursor()
    for key in update_dict: # key has to match exact vocabulary of table
        query = """UPDATE members
                   SET %s = %%s
                   WHERE clubhouse_id = %%s
                   AND member_id = %%s""" % key
        cursor.execute(query, (update_dict[key], club_id, mem_id))

    conn.commit()
    cursor.close()
    conn.close()
    return _l("Member updated successfully.") # could be more specific but that requires getting more info

# delete a specific member
def delete_specific_member(club_id, mem_id):
    conn = get_conn()
    cursor = conn.cursor()
    # set inactive in members table
    cursor.execute("""UPDATE members
                        SET active = 0
                        WHERE clubhouse_id = %s
                        AND member_id = %s""",
                        (club_id, mem_id))
    # delete from members table
#    cursor.execute("""DELETE FROM members
#                        WHERE clubhouse_id = %s
#                        AND member_id = %s""",
#                        (club_id, mem_id))
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
    conn.close()
    return _l("Member deleted successfully.") # could be more specific but that requires getting more info

# retrieve all check-ins
def get_all_checkins():
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("SELECT * FROM checkins")
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# retrieve check-ins from a certain clubhouse
def get_checkins_by_clubhouse(clubhouse_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM checkins
                      WHERE clubhouse_id = %s""", (clubhouse_id, ))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# retrieve check-ins for a given member
def get_checkins_by_member(clubhouse_id, member_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT * FROM checkins
                      WHERE clubhouse_id = %s
                      AND member_id = %s""", (clubhouse_id, member_id))
    rows = cursor.fetchall()
    cursor.close()
    conn.close()
    return rows

# changes the is_checked_in field for a given member
def change_member_checkin(member_id, clubhouse_id, checked_in):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""UPDATE members
                      SET is_checked_in = %s
                      WHERE clubhouse_id = %s
                      AND member_id = %s""", (checked_in, clubhouse_id, member_id))
    conn.commit()
    cursor.close()
    conn.close()
    return "Check-in status changed successfully."

# add a new check-in
def add_checkin(member_id, clubhouse_id):
    current_time = datetime.now()
    conn = get_conn()
    cursor = conn.cursor()
    # for testing, change later
    cursor.execute("""INSERT INTO checkins (member_id, checkin_datetime, clubhouse_id)
                      VALUES (%s, %s, %s)""",
                      (member_id, current_time, clubhouse_id))
    conn.commit()
    cursor.close()
    conn.close()
    change_member_checkin(member_id, clubhouse_id, True)

# add a new check-out, edits checkins table
def add_checkout(member_id, clubhouse_id):
    current_time = datetime.now()
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""UPDATE checkins
                      SET checkout_datetime = %s
                      WHERE member_id = %s
                      AND clubhouse_id = %s
                      AND checkout_datetime IS NULL""",
                      (current_time, member_id, clubhouse_id))
    conn.commit()
    cursor.close()
    conn.close()
    change_member_checkin(member_id, clubhouse_id, False)

# mass checkout, code repeated for efficiency
def checkout_all_from_clubhouse(clubhouse_id):
    current_time = datetime.now()
    checked_in_members = get_checked_in_members(clubhouse_id)
    conn = get_conn()
    cursor = conn.cursor()
    for member_id, mem_name in checked_in_members:
        cursor.execute("""UPDATE checkins
                          SET checkout_datetime = %s
                          WHERE member_id = %s
                          AND clubhouse_id = %s
                          AND checkout_datetime IS NULL""",
                          (current_time, member_id, clubhouse_id))
        cursor.execute("""UPDATE members
                      SET is_checked_in = %s
                      WHERE clubhouse_id = %s
                      AND member_id = %s""", (False, clubhouse_id, member_id))

    conn.commit()
    cursor.close()
    conn.close()

def enable_auto_checkout(clubhouse_id):
    conn = get_conn()
    cursor = conn.cursor()
    members = [x[0] for x in get_clubhouse_members(clubhouse_id)] # only gets list of member_ids

    for member_id in members:
        event_name = 'autocheckoutc' + str(clubhouse_id) + 'm' + str(member_id)

        # set up recurring database event: sketch things: may need to set event-scheduler=ON in mysql config file
        cursor.execute("""CREATE EVENT IF NOT EXISTS %s
                            ON SCHEDULE AT addtime(CURDATE(), '23:59:59') + INTERVAL 1 DAY ON COMPLETION PRESERVE ENABLE DO IF ((SELECT checkout_datetime FROM checkins
                                    WHERE member_id = %%s
                                    ORDER BY checkin_datetime DESC
                                    LIMIT 1) = NULL) THEN
                                    UPDATE checkins
                                        SET checkout_datetime =  CURRENT_TIMESTAMP
                                        WHERE member_id = %%s
                                        ORDER BY checkin_datetime DESC
                                        LIMIT 1;
                                END IF
                                """ % (event_name, ),
                            (member_id, member_id))
    conn.commit()
    cursor.close()
    conn.close()

# sketch mysql variable thing, recently deleted:
                            # -- SET @check_row := (SELECT checkout_datetime FROM checkins
                            # --         WHERE member_id = %%s
                            # --         ORDER BY checkin_datetime DESC
                            # --         LIMIT 1);
                            # --     SELECT @check_row;

### admin side ###

# given id number of clubhouse, get clubhouse name (either 'short_name' or 'full_name')
# given id number of clubhouse, select one specific field
# alternatively get all clubhouse data
def get_clubhouse_from_id(club_id, field="short_name"):
    conn = get_conn()
    cursor = conn.cursor()
    if field:
        query = """SELECT %s FROM clubhouses WHERE clubhouse_id = %%s""" % field
        cursor.execute(query, (club_id,))
    else: # select everything
        cursor.execute("""SELECT full_name, short_name, join_date, display_by_last FROM clubhouses WHERE clubhouse_id = %s""", (club_id,))
    club_info = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    if len(club_info) > 1:
        application.logger.error("error: found more than two clubhouses with these ids")
    elif len(club_info) < 1:
        application.logger.error("error: didn't find any clubhouse with this id")
    if field:
        return club_info[0][0]
    return club_info[0]

# analog to get_clubhouse_members, return id,name (either short or long name)
# ordered alphabetically
def get_all_clubhouses(name="short_name"):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT clubhouse_id, %s FROM clubhouses WHERE active = 1
                        ORDER BY %s""" % (name, name))
    rows = cursor.fetchall()
    conn.commit()
    cursor.close()
    conn.close()
    return rows

# check to make sure usernames are distinct
def check_distinct_clubhouse_usernames(proposed_username):
    conn = get_conn()
    cursor = conn.cursor()

    cursor.execute("""SELECT username FROM logins
                        WHERE username = %s
                        AND is_admin = 0""",
                        (proposed_username, ))
    repeats = cursor.fetchall()
    if len(repeats) > 0:
        # another clubhouse already has this nickname
        return False
    return True

# adds and creates a clubhouse, similar to add_member
def add_clubhouse(update_dict):
    conn = get_conn()
    cursor = conn.cursor()

    # create clubhouse row
    cursor.execute("""INSERT INTO clubhouses (clubhouse_id, short_name, full_name)
                        VALUES (DEFAULT, 'NULL', 'temp_full')""") # may error if other values have no default

    # get this id that we just created
    cursor.execute("""SELECT LAST_INSERT_ID()""")
    club_ids = cursor.fetchall()
    if len(club_ids) != 1:
        application.logger.error("There should only be one ID.")
        application.logger.error(club_ids)
    new_club_id = club_ids[0]

    pw = generate_password_hash(update_dict['password'])

    # create login row
    cursor.execute("""INSERT INTO logins (user_id, username, password, clubhouse_id, is_admin)
                        VALUES (DEFAULT, %s, %s, %s, DEFAULT)""",
                        (update_dict['username'], pw, new_club_id))
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
    # set short_name to full_name if short_name does not exist
    if 'short_name' not in update_dict or len(update_dict['short_name']) == 0:
        cursor.execute("""UPDATE clubhouses SET short_name = %s WHERE clubhouse_id = %s""", (update_dict['full_name'], new_club_id))
    conn.commit()
    cursor.close()
    conn.close()
    return (_l("Clubhouse added successfully."), new_club_id) # again could be more specific

def delete_clubhouse(club_id):
    conn = get_conn()
    cursor = conn.cursor()

    # get members of clubhouse (active in query pertains to member being active)
    cursor.execute("SELECT member_id FROM members WHERE clubhouse_id = %s AND active = 1", (club_id,))
    members = cursor.fetchall()

    # set members to be inactive
    for mem_id in members:
        cursor.execute("""UPDATE members
                            SET active = 0
                            WHERE clubhouse_id = %s
                            AND member_id = %s""",
                            (club_id, mem_id))

    # set clubhouse inactive (rather than deleting it)
    cursor.execute("""UPDATE clubhouses
                        SET active = 0
                        WHERE clubhouse_id = %s""",
                        (club_id, ))

    # delete clubhouse login row
    cursor.execute("""DELETE FROM logins
                        WHERE clubhouse_id = %s""",
                        (club_id, ))

    conn.commit()
    cursor.close()
    conn.close()
    return _l("Clubhouse removed successfully.")

# get login information
# on an attempted login with username username,
# retrieve the user id from table
# return user id or None if username is invalid
def get_id_from_username(username):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id FROM logins
                    WHERE username = %s""", (username,))
    users = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(users) == 0: # no such user
        return None
    if len(users) > 1:
        application.logger.error("Multiple users with this username")
    else:
        return users[0][0]

# given either the username or the id of a clubhouse account
# return club id for that account
def get_club_id_from_user(user_id = None):
    if user_id:
        conn = get_conn()
        cursor = conn.cursor()
        cursor.execute("""SELECT clubhouse_id FROM logins
                    WHERE user_id = %s""", (user_id,))
        club_ids = cursor.fetchall()
        cursor.close()
        conn.close()
        if len(club_ids) != 1:
            application.logger.error("There should be exactly one clubhouse with this user id")
        else:
            return club_ids[0][0]
    return None

# given id of clubhouse, get the corresponding user id
def get_user_id_from_club(club_id):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id FROM logins
                    WHERE clubhouse_id = %s""", (club_id,))
    user_ids = cursor.fetchall()
    cursor.close()
    conn.close()
    if len(user_ids) != 1:
        application.logger.error("Only one clubhouse should have this id.")
    else:
        return user_ids[0][0]

# given id number of user, retrieve user info or tuple of None
# if last_name is True, members will be listed by last name
# return (id, username, password hash, club_id, is_admin, last_name)
# here id is the user login id
def get_user_from_id(id_num):
    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""SELECT user_id, username, password, clubhouse_id, is_admin FROM logins
                    WHERE user_id = %s""", (id_num,))
    users = cursor.fetchall()
    if len(users) != 1:
        application.logger.error("There should be exactly one user with this user id.")
    else:
        u_id, username, password, club_id, is_admin = users[0]
        if is_admin:
            last_name = False
        else:
            # get user preference for name display order
            last_name = get_clubhouse_from_id(club_id, field="display_by_last")
        return (u_id, username, password, club_id, is_admin, last_name)
    return (None, None, None, None, None, None)

# HELPER FUNCTION: also removes empty fields
def convert_form_to_dict(form, to_remove):
    # convert to mutable dictionary
    update_dict = dict(form) # WARNING: values are in list form
    # remove all empty/unnecessary fields
    for key in update_dict:
        if type(update_dict[key]) == list and len(update_dict[key]) == 1:
            update_dict[key] = update_dict[key][0]
        # additional stupid boolean thing, I don't know a better way to handle this
        if key == "display_by_last" and update_dict[key] == 'y':
            update_dict[key] = '1'
    for field in update_dict:
        if len(update_dict[field]) == 0:
            to_remove.append(field)
    for field in to_remove:
        del update_dict[field]
    return update_dict

# set password of user id_num to password
# id_num is user id
def update_password(id_num, password):
    pw = generate_password_hash(password)

    conn = get_conn()
    cursor = conn.cursor()
    cursor.execute("""UPDATE logins
                        SET password = %s
                        WHERE user_id = %s""",
                        (pw, id_num))
    conn.commit()
    cursor.close()
    conn.close()

# update clubhouse info given clubhouse id
def update_club_info(club_id, full_name, short_name, display_by_last = None):
    conn = get_conn()
    cursor = conn.cursor()
    if len(full_name) > 0:
        cursor.execute("""UPDATE clubhouses
                            SET full_name = %s
                            WHERE clubhouse_id = %s""",
                            (full_name, club_id))
    if len(short_name) > 0:
        cursor.execute("""UPDATE clubhouses
                            SET short_name = %s
                            WHERE clubhouse_id = %s""",
                            (short_name, club_id))
    if display_by_last is not None:
        cursor.execute("""UPDATE clubhouses
                            SET display_by_last = %s
                            WHERE clubhouse_id = %s""",
                            (display_by_last, club_id))
    # join_date is mandatory on the add form
#    if join_date and len(join_date) > 0:
#        cursor.execute("""UPDATE clubhouses
#                            SET join_date = %s
#                            WHERE clubhouse_id = %s""",
#                            (join_date, club_id))
    conn.commit()
    cursor.close()
    conn.close()
