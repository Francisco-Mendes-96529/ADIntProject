from flask import Flask
from flask import render_template, request, url_for, redirect
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column, Integer, String, Date, Time
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

from flask_xmlrpcre.xmlrpcre import *

from sqlalchemy.orm import sessionmaker
from os import path

from datetime import datetime

# SQL STUFF
# SLQ access layer initialization
DATABASE_FILE = "database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine(
    "sqlite:///%s" % (DATABASE_FILE), echo=False
)  # echo = True shows all SQL calls

Base = declarative_base()


# SQLAlchemy class to store checkin data
class CheckInOut(Base):
    __tablename__ = "checkinout"
    id = Column(Integer, primary_key=True)
    userId = Column(String, nullable=False)
    # roomType = Column(String) I wish this was it
    roomId = Column(Integer, nullable=False)
    checkin = Column(Time, nullable=False)
    checkout = Column(Time)

    def __repr__(self):
        return f"id: {self.id}, roomType: {self.roomType}, roomId: {self.roomId}, checkin: {self.checkin}, checkout: {self.checkout}"


Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


def checkin(userId, roomId):
    existing_checkin = (
        session.query(CheckInOut)
        .filter(CheckInOut.userId == userId, CheckInOut.checkout.is_(None))
        .first()
    )

    if existing_checkin:
        raise Exception(f"User {userId} has already checked in and not checked out.")
    else:
        chk = CheckInOut(userId=userId, roomId=roomId, checkin=datetime.now().time())
        session.add(chk)
        session.commit()
        return f"Successufully CheckIn User {userId} to Room {roomId}."


def checkout(userId):
    chk = session.query(CheckInOut).filter_by(userId=userId, checkout=None).first()
    if chk:
        chk.checkout = datetime.now().time()
        session.commit()
        return f"Successufully CheckOut User {userId}"
    else:
        raise Exception(f"No check-in record found for userId: {userId}")


def getCheckInOut(userId):
    entries = session.query(CheckInOut).filter_by(userId=userId).all()
    data = []
    if entries:  # Check if entries is not empty
        for entry in reversed(entries):
            data.append(
                {
                    "id": entry.id,
                    "userId": entry.userId,
                    "roomId": entry.roomId,
                    "checkin": str(entry.checkin),
                    "checkout": str(entry.checkout),
                }
            )
    return data


app = Flask(__name__)


# Display CheckIn Form
@app.route("/checkin", methods=["POST", "GET"])
def checkin_page():
    return render_template("checkin.html")


# Post CheckIn Form and return success or failure
@app.route("/post_checkin", methods=["POST", "GET"])
def post_checkin():
    if request.method == "POST":
        userId = request.form.get("userId")
        roomId = request.form.get("roomId")
        try:
            s = checkin(userId, roomId)
            data = {"message": s, "action": "/checkin"}
            return render_template("success.html", data=data)
        except Exception as e:
            print(e)
            data = {"message": e, "action": "/checkin"}
            return render_template("failure.html", data=data)
    else:
        return redirect(url_for("checkin_page"))


# Display Checkout Form
@app.route("/checkout", methods=["POST", "GET"])
def checkout_page():
    return render_template("checkout.html")


# Post CheckOut Form and return success or failure
@app.route("/post_checkout", methods=["POST", "GET"])
def post_checkout():
    if request.method == "POST":
        userId = request.form.get("userId")
        try:
            s = checkout(userId)
            data = {"message": s, "action": "/checkout"}
            return render_template("success.html", data=data)
        except Exception as e:
            print(e)
            data = {"message": e, "action": "/checkout"}
            return render_template("failure.html", data=data)
    else:
        return redirect(url_for("checkout_page"))


# Display CheckInOut data for user
@app.route("/listcheckinout", methods=["POST", "GET"])
def listcheckinout():
    data = []
    if request.method == "GET":
        return render_template("listcheckinout.html", data=data)

    userId = request.form.get("userId")
    data = getCheckInOut(userId)
    return render_template("listcheckinout.html", data=data)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)
