from flask import Flask
from flask import render_template, request, url_for, redirect, jsonify
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.orm import sessionmaker, declarative_base

from os import path
from datetime import datetime

app = Flask(__name__)

# SQL Database configuration
DATABASE_FILE = "database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)
Base = declarative_base()

# Define SQLAlchemy data models: Message
class Message(Base):
    __tablename__ = "messages"
    id = Column(Integer, primary_key=True)
    from_user_id = Column(String, nullable=False)
    to_user_id = Column(String, nullable=False)
    datetime = Column(DateTime, nullable=False)
    message = Column(String, nullable=False)

    def __repr__(self):
        return f"id: {self.id}, from user: {self.from_user_id}, to user: {self.to_user_id}, date: {self.datetime}, message: {self.message}"

# Create tables for the data models in the database
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# SQL Functions
def newMessage(from_user_id, to_user_id, message):
    msg = Message(from_user_id=from_user_id, to_user_id=to_user_id, datetime=datetime.now(), message=message)
    session.add(msg)
    session.commit()

def getSentMessages(user_id):
    return session.query(Message).filter_by(from_user_id=user_id).all()
    
def getReceivedMessages(user_id):
    return session.query(Message).filter_by(to_user_id=user_id).all()

# HTML routes
@app.route("/")
def index_page():
    return render_template("index.html")

@app.route('/send_message', methods=['GET', 'POST'])
def send_message():
    return render_template('send_message.html')

@app.route('/post_message', methods=['GET', 'POST'])
def post_message():
    if request.method == 'POST':
        from_user_id = request.form.get('from-user-id')
        to_user_id = request.form.get('to-user-id')
        message = request.form.get('message-text')
        newMessage(from_user_id, to_user_id, message)
        return render_template('sent_successful.html')
    else:
        return redirect(url_for('send_message'))

@app.route('/sent_messages', methods=['GET', 'POST'])
def sent_messages():
    if request.method == 'POST':
        user_id = request.form.get('user-id')
        return redirect(url_for('sent_messages', user_id=user_id))
    else:
        user_id = request.args.get('user_id')
        if user_id:
            msg_list = reversed(getSentMessages(user_id))
            return render_template('sent_messages.html', msg_list=msg_list, user_id_to_prefill=user_id)
        else:
            return render_template('sent_messages.html')

@app.route('/received_messages', methods=['GET', 'POST'])
def received_messages():
    if request.method == 'POST':
        user_id = request.form.get('user-id')
        return redirect(url_for('received_messages', user_id=user_id))
    else:
        user_id = request.args.get('user_id')
        if user_id:
            msg_list = reversed(getReceivedMessages(user_id))
            return render_template('received_messages.html', msg_list=msg_list, user_id_to_prefill=user_id)
        else:
            return render_template('received_messages.html')

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5005)
