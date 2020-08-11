import sqlite3
import dateparser
from datetime import datetime, timedelta, date
from mail import send_mail

# path="/home/traincheck/mysite/"
path=""
conn = sqlite3.connect(path+'store.db')
c = conn.cursor()

now = datetime.now()
hours = timedelta(hours=24)
cutoff= now-hours
c.execute("SELECT * from Escort where datetime_created > '%s'" % cutoff)

unique = []
for i in c:
  train_no = i[2]
  origin_date = i[12]
  uni = str(train_no)+origin_date
  unique.append(uni)

segments = len(unique)
trains = len(set(unique))
    
conn.close()

# mail section

sender = {
  'email': "vivekkaushalauto@gmail.com",
  'password':"autoaccount",
  'identity':"Train Escort Check",
  'smtp':"smtp.gmail.com",
}
recipients = ['ascpsrb@gmail.com']
subject = 'Daily Report : '+str(now.date())
content = "Hello,<br/> Report generated on : "+str(now.date())+\
"<br/>Number of Segments Escorted : "+str(segments) +\
 "<br/>Number of Trains Escorted : "+str(trains)+\
"<br/>Regards,<br/>Train Check Escort<br/>"+\
"<br/><a href='http://vivekkaushal.com'>vivekkaushal.com</a>"


send_mail(sender, recipients, subject, content)
print('mails sent on', now)
print ('done')