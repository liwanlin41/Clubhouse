# helper functions for database operations, all functions with db accesses should be here

from app import conn

# retrieve cursor for MySQL database defined in env vars
def get_cursor():
    cursor = conn.cursor()
    return cursor

# retrieve all members
def get_all_members():
    cursor = get_cursor()
    cursor.execute("SELECT * FROM members")
    rows = cursor.fetchall()
    for row in rows:
        print(row)
    cursor.close()
    return rows

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
