from flask import Flask, render_template, url_for, redirect, request, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dateutil import tz
from datetime import datetime, timedelta
import random , string
import json
import requests

# initializing the App and database
app = Flask(__name__)
SESSION_TYPE = 'filesystem'
app.config['SQLALCHEMY_DATABASE_URI']='sqlite:///store.db'
db = SQLAlchemy(app)

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



class Escort(db.Model):
  transaction_id = db.Column(db.String, primary_key=True)
  datetime_created = db.Column(db.DateTime, default=datetime.now())
  train_number = db.Column(db.Integer)
  origin = db.Column(db.String)
  terminating = db.Column(db.String)
  current = db.Column(db.String)
  escort_name = db.Column(db.String)
  escort_phone = db.Column(db.String)
  zone = db.Column(db.String)
  updater_name = db.Column(db.String)
  escort_from = db.Column(db.String)
  escort_to = db.Column(db.String)
  origin_date = db.Column(db.String)

def generate_random_string(stringLength=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/')
def index():
  return render_template('index.html', error=False)

@app.route('/all')
def all():
  format = "%Y-%m-%d %H:%M:%S %Z%z"
  three_days_ago = datetime.now() - timedelta(3)
  output = Escort.query.filter(Escort.datetime_created>=three_days_ago).order_by(Escort.datetime_created.desc()).all()
  from_zone = tz.gettz('UTC')
  to_zone = tz.gettz('Asia/Kolkata')
  for i in output:
    naive_date = i.datetime_created.replace(tzinfo=from_zone)
    i.datetime_created = naive_date.astimezone(to_zone).strftime(format)
  return render_template('all.html',output=output)

@app.route('/data')
def data():
  train_no = session.get('train_no')
  three_days_ago = datetime.now() - timedelta(4)
  # output = Escort.query.filter(Escort.train_number==train_no).filter((Escort.origin_date>=three_days_ago) | (Escort.origin_date == None)).order_by(Escort.datetime_created.desc()).all()
  output = Escort.query.filter(Escort.train_number==train_no).filter(Escort.origin_date>=three_days_ago).order_by(Escort.datetime_created.desc()).all()

  print(output)

  if len(output) == 0:
    return redirect('/error')

  try:
    final_output = prepare_output(output)
    return render_template('data.html', output=final_output)
  except:
    return redirect('/error')

@app.route('/error')
def error():
    return render_template('index.html', error=True)


@app.route('/get_train_no')
def get_train_no():
  train_no = request.args.get('train_no')
  session['train_no'] = train_no
  return redirect('/data')

@app.route('/get_data')
def get_data():
  train_no = int(request.args.get('train_no'))
  origin = request.args.get('origin')
  origin_date = request.args.get('origin_date')
  terminating = request.args.get('terminating')
  current = request.args.get('current')
  escort_phone = request.args.get('escort_phone')
  escort_name = request.args.get('escort_name')
  zone = request.args.get('zone')
  name = request.args.get('name')
  escort_from = request.args.get('escort_from')
  escort_to = request.args.get('escort_to')
  eid = generate_random_string(15)
  date = datetime.now()
  new_escort = Escort(transaction_id=eid, datetime_created=date,\
  train_number=train_no,origin=origin,origin_date=origin_date,terminating=terminating,\
  current=current,escort_name=escort_name,escort_phone=escort_phone,\
  zone=zone, updater_name=name, escort_from=escort_from, escort_to=escort_to)
  db.session.add(new_escort)
  db.session.commit()

  return redirect('/done')

@app.route('/done')
def done():
  return render_template('done.html')

@app.route('/password')
def password():
  return render_template('password.html',wrong=False)

@app.route('/verify')
def verify():
  key = '<pass>'
  entered = request.args.get('entered')
  if entered == key:
    return redirect('/enter')
  else:
    return render_template('password.html',wrong=True)

@app.route('/enter')
def enter():
  return render_template('enter.html')

if __name__ == "__main__":
  app.run(debug=True)


