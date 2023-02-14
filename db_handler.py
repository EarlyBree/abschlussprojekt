import sqlite3

con = sqlite3.connect('jobs.db')

cur = con.cursor()

# cur.execute('''CREATE TABLE finishedjobs (task text, status text, start text)''')
# cur.execute('''CREATE TABLE paused (id int, task boolean)''')

# cur.execute("INSERT INTO paused VALUES (1, 1)")
# cur.execute('DELETE FROM finishedjobs')
con.commit()
con.close()