import sqlite3

conn = sqlite3.connect('database.db')
print("Opened database successfully")
# conn.execute("drop table contacts")
# conn.execute("create table contacts(name TEXT, phone int primary key, email TEXT, last_sent_time datetime, create_time datetime default current_timestamp);")

# a = conn.execute("update contacts set last_sent_time=null;")
a = conn.execute("select * from contacts;")
print(a.fetchall())
conn.commit()

print("Table created successfully")
conn.close()
