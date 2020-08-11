import time
import smtplib
import mimetypes
import email
import email.mime.application
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

def send_mail(sender, recipients, subject, content,):
	for recipient in recipients:
		print("SENDING to %s" %(recipient))

		# Create a text/plain message
		msg = MIMEMultipart()
		msg['Subject'] = subject
		msg['From'] = sender['identity'] + " <" + sender['email'] + ">"
		msg['To'] = recipient
		msg.preamble = 'This is a multi-part message in MIME format.'

		# Content for the email
		body = MIMEText(content, 'html')
		msg.attach(body)

		# Attachment
		# filename=filename_with_path
		# with open(filename) as fp:
		# 	att = email.mime.application.MIMEApplication(fp.read(),_subtype="csv")
		# att.add_header('Content-Disposition','attachment',filename=filename)
		# msg.attach(att)

		# send via Gmail server
		s = smtplib.SMTP(sender['smtp'])
		s.starttls()
		s.login(sender['email'], sender['password'])
		s.sendmail(sender['email'], recipient, msg.as_string())
		s.quit()
		time.sleep(2)
	return

