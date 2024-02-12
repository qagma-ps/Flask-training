from datetime import datetime

from werkzeug.security import generate_password_hash

from apps.app import db


# Create User class inherited db.Model
class User(db.Model):
    # Table Name
    __tablename__ = "users"
    # Column
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Pass word property
    @property
    def password(self):
        raise AttributeError("読み取り付加")

    # Set Hashed password via Setter function
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)
