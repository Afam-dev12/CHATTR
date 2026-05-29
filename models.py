from flask_sqlalchemy import SQLAlchemy
from flask_login import UserMixin
from datetime import datetime 

db = SQLAlchemy()

class User(UserMixin, db.Model):

    id = db.column(db.Integer, primary_keys=True)

    username = db.Column(
        db.String(50),
        unique=True,
        nullable=False
    )

    email = db.column(
        db.String(120),
        unique=True,
        nullable=False
    )

    password = db.column(
        db.String(200),
        nullable=False
    )

    profile_pic = db.column(
        db.String(200),
        default="default.png"
    )

    bio = db.Column(
        db.String(300),
        default="Hello"
    )

    online = db.Column(
        db.Boolean,
        default="dark"
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

class Message(db.Model):

    id =db.Column(db.Integer, primary_key=True)   

    sender_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    ) 

    receiver_id = db.Column(
        db.Integer,
        db.ForeignKey("user.id"),
        nullable=False
    )

    content = db.Column(
        db.Text,
        nullable=True
    )

    seen = db.column(
        db.Boolean,
        default=False
    )

    timestamp = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )
