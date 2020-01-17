# helper functions for database operations, all functions with db accesses should be here

from app import conn

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
    cursor.execute("SELECT member_id, first_name, last_name FROM members WHERE clubhouse_id = %s ORDER BY %s" %(clubhouse_id, sorting))
    rows = cursor.fetchall()
#    for row in rows: # for debugging purposes?
#        print(row)
    cursor.close()
    return rows

# retrieve a specific member: returns the whole row
def get_specific_member(clubhouse_id, member_id):
    cursor = get_cursor()
    cursor.execute("SELECT * FROM members WHERE clubhouse_id = %s AND member_id = %s", (clubhouse_id, member_id))
    member = cursor.fetchall()
    if len(member) > 1:
        print("error: found more than two members with these ids") # shouldn't happen
    return member[0]

# retrieve only certain members (for filtering)
def query_members():
    pass

# register a new member
def add_member():
    cursor = get_cursor()
    # for testing, change later
    cursor.execute("""INSERT INTO members (first_name, last_name, clubhouse_id)
                    VALUES ('carolyn', 'mei', 1)""")
    conn.commit()
    cursor.close()

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
def add_checkin():
    pass

# add a new check-out, edits checkins table
def add_checkout():
    pass
