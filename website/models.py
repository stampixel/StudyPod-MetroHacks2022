from . import db
from flask_login import UserMixin
from datetime import datetime
from sqlalchemy.sql import func


# Database column for notes
class Notes(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    url_id = db.Column(db.String(128))
    title = db.Column(db.String(50))
    content = db.Column(db.String(10000))
    date = db.Column(db.DateTime(timezone=True), default=func.now())

    public = db.Column(db.Boolean, default=True, nullable=False)

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Checklist database
class Checklist(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.String(30))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# Profile database (unused for now)
class Profile(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    pfp = db.Column(db.String(500))
    about_me = db.Column(db.String(2000))

    user_id = db.Column(db.Integer, db.ForeignKey('user.id'))


# User database
class User(db.Model, UserMixin):  # user information, username, password, etc
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(24), unique=True, nullable=False)
    password = db.Column(db.String(150))

    note = db.relationship('Notes')
    profile = db.relationship('Profile')
    checklist = db.relationship('Checklist')
