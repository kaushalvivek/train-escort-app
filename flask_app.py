from flask import Flask, render_template, url_for, redirect, request, jsonify, session
from flask_session import Session
from flask_sqlalchemy import SQLAlchemy
from dateutil import tz
from datetime import datetime
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

def generate_random_string(stringLength=10):
  letters = string.ascii_lowercase
  return ''.join(random.choice(letters) for i in range(stringLength))

@app.route('/')
def index():
  return render_template('index.html')

@app.route('/data')
def data():
  train_no = session.get('train_no')
  output = Escort.query.filter(Escort.train_number==train_no).order_by(Escort.datetime_created).all()
  from_zone = tz.gettz('UTC')
  to_zone = tz.gettz('Asia/Kolkata')
  format = "%Y-%m-%d %H:%M:%S %Z%z"

  try:
    naive_date = output[-1].datetime_created.replace(tzinfo=from_zone)
    indian_datetime = naive_date.astimezone(to_zone).strftime(format)
    return render_template('data.html', latest=output[-1], all=output,indian_datetime=indian_datetime)
  except:
    return render_template('error.html')

@app.route('/error')
def error():
  train_no = session.get('train_no')
  output = Escort.query.filter(Escort.train_number==train_no).order_by(Escort.datetime_created).all()
  try:
    return render_template('data.html', latest=output[-1], all=output)
  except:
    return render_template('error.html')


@app.route('/get_train_no')
def get_train_no():
  train_no = request.args.get('train_no')
  session['train_no'] = train_no
  return redirect('/data')

@app.route('/get_data')
def get_data():
  train_no = int(request.args.get('train_no'))
  origin = request.args.get('origin')
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
  train_number=train_no,origin=origin,terminating=terminating,\
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
  key = 'rpfvinay'
  return render_template('password.html',key=key)

@app.route('/enter')
def enter():
  return render_template('enter.html')

if __name__ == "__main__":
  app.run(debug=True)


