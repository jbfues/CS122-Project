#A script to make email_list table in db.sql
# run the following command to use:
#
#   python make_email_list.py

import sqlite3

db_file = '/home/student/CS122-Project/db.sql'
conn = sqlite3.connect(db_file)
c = conn.cursor()

c.execute('''CREATE TABLE email_list
    (license text, email text)''')

#save the changes to db file
conn.commit()
conn.close()