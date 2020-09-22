from flask import Flask, render_template, url_for, redirect, request, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dateutil import tz
from datetime import datetime, timedelta
import random , string
import json

# initializing the App and database
app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///store.db'
db = SQLAlchemy(app)

SECRET_KEY="dfjaiofanfdklasnfv1231sdjfwdaipfoj123awd"
zones = ['CR','ER','ECR','NR','NCR','NER','NFR','SR','SCR','SER','SECR','SWR','WR','WCR','KR']
train_types=['15 Pairs','Shramik Special','100 Pairs']
password = "password"

app.config.from_object(__name__)
Session(app)

def prepare_output(output):
  entries = []
  # convert queries to objects
  for obj in output:
    entry = {
      'train_no': obj.train_number,
      'escort_name':obj.escort_name,
      'escort_phone':obj.escort_phone,
      'escort_from':obj.escort_from,
      'escort_to':obj.escort_to,
      'current':obj.current,
      'datetime_created':obj.datetime_created,
      'origin':obj.origin,
      'terminating':obj.terminating,
      'origin_date':obj.origin_date,
      'updater_name':obj.updater_name,
      'zone':obj.zone
    }
    # append query to objects
    entries.append(entry)
  
  # get unique dates
  origin_dates = {entry['origin_date'] for entry in entries}
  # to store final output
  final_output = []

  # get latest entry for each unique date
  for date in origin_dates:
    all_with_date = []
    for i in entries:
      if (i['origin_date']==date):
        all_with_date.append(i)
    all_with_date.sort(key=lambda x:x['datetime_created'], reverse=True)
    # add latest entry for each unique date to final_output
    final_output.append(all_with_date[0])

  # prepare final output for indian date time
  final_output.sort(key=lambda x:x['origin_date'], reverse=True)
  from_zone = tz.gettz('UTC')
  to_zone = tz.gettz('Asia/Kolkata')
  format = "%Y-%m-%d %H:%M:%S %Z%z"
  naive_date = [i['datetime_created'].replace(tzinfo=from_zone) for i in final_output]
  indian_datetime = [i.astimezone(to_zone).strftime(format) for i in naive_date]
  for i in range(len(final_output)):
    final_output[i]['datetime_created'] = indian_datetime[i]
    if final_output[i]['origin_date'] == None:
      final_output[i]['origin_date'] = '* date not specified *'
  return final_output


class Entry(db.Model):
  transaction_id = db.Column(db.String, primary_key=True)
  datetime_created = db.Column(db.DateTime, default=datetime.now())
  train_no = db.Column(db.Integer)
  train_type = db.Column(db.String)
  origin_date = db.Column(db.DateTime)
  origin_zone = db.Column(db.Boolean)
  terminating_zone= db.Column(db.Boolean)

  escort_name = db.Column(db.String)
  escort_phone = db.Column(db.String)
  escort_count = db.Column(db.Integer)
  escort_from = db.Column(db.String)
  escort_to = db.Column(db.String)

  updater_name = db.Column(db.String)
  zone = db.Column(db.String)

def generate_random_string(stringLength=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/')
def index():
  # if logged in, redirect to data entry page
  if 'token' in session and session.get('token')==SECRET_KEY:
    return render_template('enter.html', \
      name=session.get('name'), zone=session.get('zone'), train_types=train_types)
  # if not logged in, redirect to login
  return render_template('login.html', zones=zones, error=False)

@app.route('/error')
def error():
  if 'token' in session and session.get('token')==SECRET_KEY:
    return redirect('/')
  return render_template('login.html', zones=zones, error=True)

@app.route('/verify')
def verify():
  if 'token' in session and session.get('token')==SECRET_KEY:
    return redirect('/')
  if request.args.get('password') == password:
    session['name']=request.args.get('name')
    session['zone']=request.args.get('zone')
    session['token']=SECRET_KEY
    return redirect('/')
  else:
    return redirect('/error')

@app.route('/get_data')
def get_data():
  if 'token' in session and session.get('token')==SECRET_KEY:
    train_no = int(request.args.get('train_no'))
    train_type = request.args.get('train_type')
    origin_date = request.args.get('origin_date')
    origin_zone = request.args.get('origin')
    terminating_zone = request.args.get('terminating')

    escort_phone = request.args.get('escort_phone')
    escort_name = request.args.get('escort_name')
    escort_count = request.args.get('escort_count')
    escort_from = request.args.get('escort_from')
    escort_to = request.args.get('escort_to')
    
    updater_name = session.get('updater')
    zone = session.get('zone')
    stamp = datetime.now()
    tran_id = generate_random_string(15)

    new_entry = Entry(
      transaction_id=tran_id, datetime_created=stamp,updater_name=updater_name,zone=zone,\
      train_no=train_no,train_type=train_type,origin_date=origin_date,\
      origin_zone=origin_zone, terminating_zone=terminating_zone,\
      escort_name=escort_name,escort_phone=escort_phone,escort_count=escort_count,\
      escort_from=escort_from, escort_to=escort_to)
    db.session.add(entry)
    db.session.commit()

    return redirect('/done')
  else:
    return redirect('/')

@app.route('/logout')
def logout():
  session.clear()
  return redirect('/')

@app.route('/help')
def help():
  return render_template('help.html')

if __name__ == "__main__":
  app.run(debug=True)


