# Consider importing os module here
from sqlalchemy import create_engine
from flask_sqlalchemy import SQLAlchemy
import json
from .test_database_setup import MOVIES, ACTORS
import os

database_name = "castingagency"

#default path: postgresql://postgres@localhost:5432/castingagency
#database_path = os.environ.get("DATABASE_URL", "postgresql://postgres@{}/{}".format('localhost:5432', database_name))

database_path = "postgresql://rzgycskfuglwnp:8ad0e6c8ec5f339f1eda0de9015446930f742236fb019509455f9dfb3f2958eb@ec2-44-193-150-214.compute-1.amazonaws.com:5432/dfk5qivnqiqkh1"

db = SQLAlchemy()

'''
setup_db(app)
    binds a flask application and a SQLAlchemy service
'''

def setup_db(app, database_path=database_path):
    app.config["SQLALCHEMY_DATABASE_URI"] = database_path
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    db.app = app
    db.init_app(app)
    db.create_all()

# intializes databases with dummy data for testing purposes
def init_db_data():
    db.drop_all()
    db.create_all()

    for movie in MOVIES:
        new_movie = Movie(
            title=movie['title'],
            release=movie['release']
        )

        new_movie.insert()

    for actor in ACTORS:
        new_actor = Actor(
            name=actor['name'],
            age=actor['age'],
            gender=actor['gender'])

        new_actor.movie_id = actor['movie_id']
        new_actor.insert()

#MODELS

class Movie(db.Model):
    __tablename__ = 'Movie'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String, nullable=False)
    release = db.Column(db.DateTime, nullable=False)  # date Movie is released

    # MAY NOT BE NECESSARY, IN FACT THIS NOT BE A RELATIONSHIP BETWEEN THE TWO
    # CLASSES
    actors = db.relationship('Actor', backref='movie', lazy=True)

    def __init__(self, title, release):
        self.title = title
        self.release = release

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'title': self.title,
            'release': self.release
        }


class Actor(db.Model):
    __tablename__ = 'Actor'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String, nullable=False)
    age = db.Column(db.Integer, nullable=False)
    gender = db.Column(db.String, nullable=False)

    # actor could currently not be assigned to a movie, so nullable is True
    movie_id = db.Column(db.Integer, db.ForeignKey('Movie.id'), nullable=True)

    def __init__(self, name, age, gender):
        self.name = name
        self.age = age
        self.gender = gender

    def insert(self):
        db.session.add(self)
        db.session.commit()

    def update(self):
        db.session.commit()

    def delete(self):
        db.session.delete(self)
        db.session.commit()

    def format(self):
        return {
            'id': self.id,
            'name': self.name,
            'age': self.age,
            'gender': self.gender,
            'current_movie': self.movie.title,
            'current_movie_id': self.movie.id
        }
