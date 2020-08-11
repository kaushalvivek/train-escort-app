'''
delete week old entries from table
'''
import sqlite3
from datetime import datetime, timedelta, date

path="/home/traincheck/mysite/"
conn = sqlite3.connect(path+'store.db')
c = conn.cursor()

today = date.today()
week = timedelta(days=7)
cutoff= today-week
c.execute("DELETE FROM Escort WHERE datetime_created <= '%s'" % cutoff)
conn.commit()
conn.close()