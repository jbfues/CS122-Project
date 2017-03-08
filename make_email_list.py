import sqlite3

db_file = '/home/student/CS122-Project/db.sql'
conn = sqlite3.connect(db_file)
c = conn.cursor()

c.execute('''CREATE TABLE email_list
    (license text, email text)''')

#save the changes to db file
conn.commit()
conn.close()