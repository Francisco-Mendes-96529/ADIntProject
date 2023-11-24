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

# SQLAlchemy Data Classes


# Stores Restaurant Data
class Restaurant(Base):
    __tablename__ = "restaurant"
    id = Column(Integer, primary_key=True)
    name = Column(String)

    def __repr__(self):
        return f"id: {self.id}, name: {self.name}, menu: {self.menu}"


# Stores Menu Data
class Menu(Base):
    __tablename__ = "menus"
    id = Column(Integer, primary_key=True)
    food = Column(String, nullable=False)
    restaurantId = Column(Integer, ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", back_populates="menu")


Restaurant.menu = relationship("Menu", order_by=Menu.id, back_populates="restaurant")


# Stores Ratings Data
class Ratings(Base):
    __tablename__ = "ratings"
    id = Column(Integer, primary_key=True)
    evaluation = Column(String, nullable=True)
    rating = Column(Integer, nullable=False)
    userId = Column(String, nullable=False)  # TODO ligar com a user table

    restaurantId = Column(Integer, ForeignKey("restaurant.id"))
    restaurant = relationship("Restaurant", back_populates="ratings")

    menuId = Column(Integer, ForeignKey("menus.id"))
    menu = relationship("Menu", back_populates="ratings")


Restaurant.ratings = relationship(
    "Ratings", order_by=Ratings.id, back_populates="restaurant"
)

Menu.ratings = relationship("Ratings", order_by=Ratings.id, back_populates="menu")


Base.metadata.create_all(engine)  # Create tables for the data models

Session = sessionmaker(bind=engine)
session = Session()


# Create new Rating
def newRating(userId, resId, evaluation, rating):
    try:
        rating = Ratings(
            userId=userId, evaluation=evaluation, rating=rating, restaurantId=resId
        )
        session.add(rating)
        session.commit()
    except Exception as e:
        session.rollback()
        # If an exception occurs, log the error for debugging purposes
        print(f"Error in newRating: {str(e)}")
        raise e  # Reraise the exception to propagate it up


app = Flask(__name__)


# Main Page, displays all Restaurants
@app.route("/", methods=["GET", "POST"])
def index_page():
    restaurants = session.query(Restaurant).all()
    resData = []
    for res in restaurants:
        resData.append({"name": res.name, "resId": res.id})
    return render_template("index.html", data=resData)


# Displays Menu of a Restaurant
@app.route("/restaurant", methods=["POST", "GET"])
def restaurant_page():
    if request.method == "POST":
        resId = request.form.get("restaurant_id")
        restaurant = session.query(Restaurant).filter(Restaurant.id == resId).first()
        menuData = []
        for menu in restaurant.menu:
            menuData.append({"food": menu.food})
        return render_template("restaurant.html", data=menuData)
    else:
        return redirect(url_for("index_page"))


# Displays Evaluation Form
@app.route("/evaluate", methods=["POST", "GET"])
def evaluate_page():
    if request.method == "POST":
        resId = request.form.get("restaurant_id")
        # TODO : get the user id to input on the evaulation
        restaurant = session.query(Restaurant).filter(Restaurant.id == resId).first()
        resData = {"resName": restaurant.name, "resId": restaurant.id}
        return render_template("evaluate.html", data=resData)
    else:
        return redirect(url_for("index_page"))


# Posts Evaluation and returns success or failure
@app.route("/post_evaluate", methods=["POST", "GET"])
def post_evaluate():
    if request.method == "POST":
        userId = request.form.get("userId")
        restaurantId = request.form.get("restaurantId")
        evaluation = request.form.get("evaluation")
        rating = request.form.get("rating")

        try:
            newRating(userId, restaurantId, evaluation, rating)
        except Exception:
            # If an error occurs in newRating, return to "evaluate_failed.html"
            return render_template("evaluate_failed.html")

        return render_template("evaluate_successful.html")
    else:
        return redirect(url_for("index_page"))


# RPC STUFF ADMIN
handler = XMLRPCHandler("api")
handler.connect(app, "/api")


# Create New Restaurant
@handler.register
def newRestaurant(name):
    res = Restaurant(name=name)
    session.add(res)
    session.commit()
    return name


# Create New Menu
@handler.register
def newMenu(food, restaurantId):
    res = session.query(Restaurant).filter_by(id=restaurantId).first()
    if res:
        menu = Menu(food=food, restaurantId=restaurantId)
        session.add(menu)
        session.commit()
        return f"Menu created: resId: {restaurantId}, food: {food}"
    else:
        return f"Restaurant with id {restaurantId} not found."


# Del Restaurant
@handler.register
def delRestaurant(resId):
    try:
        # Query for the message by its ID
        res = session.query(Restaurant).filter_by(id=resId).first()

        if res:
            # If the message exists, delete it
            session.delete(res)
            session.commit()
            return f"Restaurant with ID {resId} deleted successfully."
        else:
            return f"Message with ID {resId} not found."

    except Exception as e:
        session.rollback()
        return e


# Del Menu
@handler.register
def delMenu(menuId):
    try:
        # Query for the message by its ID
        menu = session.query(Menu).filter_by(id=menuId).first()

        if menu:
            # If the message exists, delete it
            session.delete(menu)
            session.commit()
            return f"Menu with ID {menuId} deleted successfully."
        else:
            return f"Menu with ID {menuId} not found."

    except Exception as e:
        session.rollback()
        return e


# Get Restaurants
@handler.register
def getRestaurant():
    restaurants = session.query(Restaurant).all()
    # Convert the data to a list of dictionaries
    data = []
    for res in restaurants:
        data.append(
            {"id": res.id, "name": res.name, "menu": [menu.food for menu in res.menu]}
        )
    return data


# Get Ratings for Restaurant
@handler.register
def getRatings(resId):
    res = session.query(Restaurant).filter_by(id=resId).first()
    if res:
        ratings = session.query(Ratings).filter(Ratings.restaurantId == resId)
        # Convert the data to a list of dictionaries
        data = []
        for rat in ratings:
            data.append(
                {
                    "id": rat.id,
                    "User Id": rat.userId,
                    "Evaluation": rat.evaluation,
                    "Rating": rat.rating,
                }
            )
        return data
    else:
        return None


# Get Menu for Restaurant
@handler.register
def getMenu(resId=None):
    if resId:
        menu = session.query(Menu).filter(Menu.restaurantId == resId)
        # Convert the data to a list of dictionaries
        data = []
        for entry in menu:
            data.append({"id": entry.id, "Food": entry.food})
        return data
    else:
        restaurants = session.query(Restaurant).all()
        # Convert the data to a list of dictionaries
        data = []
        for res in restaurants:
            resData = []
            for entry in res.menu:
                resData.append({"id": entry.id, "Food": entry.food})
            data.append({"resId": res.id, "menu": resData})

        return data


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)
