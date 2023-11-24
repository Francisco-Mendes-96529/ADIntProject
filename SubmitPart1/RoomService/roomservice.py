from flask import Flask
from flask import render_template, request, abort
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy import ForeignKey
from sqlalchemy.orm import declarative_base, relationship
from sqlalchemy.orm import sessionmaker

from flask_xmlrpcre.xmlrpcre import *

from os import path
from datetime import datetime
import json

app = Flask(__name__)

# Setup RPC ADMIN
handler = XMLRPCHandler("api")
handler.connect(app, "/api")

# SQL Database configuration
DATABASE_FILE = "database.sqlite"
db_exists = False
if path.exists(DATABASE_FILE):
    db_exists = True
    print("\t database already exists")

engine = create_engine("sqlite:///%s" % (DATABASE_FILE), echo=False)
Base = declarative_base()

# Define SQLAlchemy data models: Space, Course, and Event
class Space(Base):
    __tablename__ = 'spaces'

    id = Column(Integer, primary_key=True)
    name = Column(String)
    
    # Create a dictionary with all the attributes of Space Class
    def to_dict(self):
        space_dict = {
            'id': self.id,
            'name': self.name,
            'events': [event.to_dict() for event in self.events] if self.events else None
        }
        return space_dict
    
    # Create a simpler dictionary with some attributes of Space Class
    def to_dict_simple(self):
        space_dict = {
            'id': self.id,
            'name': self.name,
        }
        return space_dict
    
class Course(Base):
    __tablename__ = 'courses'

    id = Column(Integer, primary_key=True)
    acronym = Column(String)
    name = Column(String)

    events = relationship('Event', back_populates='course', cascade='all, delete-orphan')

    # Create a dictionary with all the attributes of Course Class
    def to_dict(self):
        course_dict = {
            'id': self.id,
            'acronym': self.acronym,
            'name': self.name,
        }
        return course_dict

class Event(Base):
    __tablename__ = 'events'

    id = Column(Integer, primary_key=True)
    weekday = Column(String)
    period_start = Column(DateTime)
    period_end = Column(DateTime)
    info = Column(String)

    space_id = Column(Integer, ForeignKey('spaces.id'))
    space = relationship('Space', back_populates='events')

    course_id = Column(Integer, ForeignKey('courses.id'))
    course = relationship('Course', back_populates='events')

    # Create a dictionary with detailed attributes of Event Class
    def to_dict(self):
        event_dict = {
            'id': self.id,
            'start': self.period_start.strftime("%H:%M"),
            'end': self.period_end.strftime("%H:%M"),
            'weekday': self.weekday,
            'day': self.period_start.strftime("%d/%m/%Y"),
            'period' : {
                'start': self.period_start.strftime("%d/%m/%Y %H:%M"),
                'end': self.period_end.strftime("%d/%m/%Y %H:%M"),
            },
            'info': self.info,
            'course': self.course.to_dict() if self.course else None
        }
        return event_dict

    # Create a simpler dictionary with some attributes of Event Class
    def to_dict_simple(self):
        event_dict = {
            'id': self.id,
            'weekday': self.weekday,
            'period' : {
                'start': self.period_start.strftime("%d/%m/%Y %H:%M"),
                'end': self.period_end.strftime("%d/%m/%Y %H:%M"),
            },
            'info': self.info,
            'course': self.course.acronym if self.course else None
        }
        return event_dict

Space.events = relationship('Event', order_by=Event.period_start, back_populates='space', cascade='all, delete-orphan')

# Create tables for the data models in the database
Base.metadata.create_all(engine)

Session = sessionmaker(bind=engine)
session = Session()

# SQL Functions
# SPACE
@handler.register
def newSpace(id, name):
    # Confirm space not exists
    space = getSpaceById(id)
    if space:
        return f"Space with Id {id} already exists.\n{space.to_dict_simple()}"
    else:
        space = Space(id=id, name=name)
        session.add(space)
        session.commit()
        return json.dumps(space.to_dict_simple())

def getSpaces():
    return session.query(Space).all()

@handler.register
def getSpacesDict():
    spaces = getSpaces()
    # Convert the spaces to a list of json dictionaries
    spaces_list = [json.dumps(space.to_dict_simple()) for space in spaces]
    return spaces_list

def getSpaceById(id):
    return session.query(Space).filter_by(id=id).first()

# EVENT
@handler.register
def updateSchedule(data):
    try:
        # Convert JSON data to Python data
        data = json.loads(data)
        space_id = data['id']
        space = getSpaceById(space_id)

        if space:
            if space.events:
                # if space exists and has events, delete events
                for event in space.events: session.delete(event)
        else:
            return f"Space with Id {space_id} not found. Please add it first."

        # Confirm the data has an 'events' category
        if 'events' in data:
            for event_data in data['events']:
                # Only save the events that are of type 'LESSON'
                if event_data['type'] == 'LESSON':
                    course_data = event_data['course']
                    # Filter the wanted 'Course' attributes from 'course' data 
                    course_data_filtered = getCourseDataFiltered(course_data)
                    # Define a new Course by the keys/values of a dictionary
                    course = Course(**course_data_filtered)
                    session.merge(course)

                    # Filter the wanted 'Event' attributes from 'event' data 
                    event_data_filtered = getEventDataFiltered(event_data)
                    # Define a new Event by the keys/values of a dictionary
                    event = Event(**event_data_filtered, space_id=space_id, course_id=course.id)
                    session.add(event)
        else:
            raise Exception("No events found.")

        session.commit()

        return "Schedule updated successfully."

    except Exception as e:
        session.rollback()
        return f"Error updating space schedule: {e}"
    
@handler.register
def getScheduleDictBySpace(space_id):
    space = getSpaceById(space_id)
    if space:
        # Convert the events to a list of json dictionaries
        events_list = [json.dumps(event.to_dict_simple()) for event in space.events]
        return events_list
    else:
        return None # Verification made in admin app


# Define helper functions for filtering data
def getCourseDataFiltered(data):
    allowed_attributes = ['id', 'acronym', 'name']
    # Create a new dictionary with only the allowed attributes
    filtered_data = {key: data[key] for key in allowed_attributes if key in data}
    return filtered_data

def getEventDataFiltered(data):
    allowed_attributes = ['weekday', 'info']
    # Create a new dictionary with only the allowed attributes
    filtered_data = {key: data[key] for key in allowed_attributes if key in data}
    if 'period' in data:
        filtered_data.update({
            f"period_{time}": datetime.strptime(data['period'][time], "%d/%m/%Y %H:%M") for time in data['period']
        })
    return filtered_data

# HTML routes
@app.route("/")
def spaces_page():
    spaces = getSpaces()
    return render_template("spaces.html", spaces=spaces)

@app.route("/schedule/<space_id>")
def schedule_page(space_id):
    space = getSpaceById(space_id)
    if space:
        return render_template('schedule.html', space_dict=space.to_dict())
    else:
        return abort(404) # return Not Found

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=5003)
