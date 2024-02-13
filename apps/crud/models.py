from datetime import datetime

from flask_login import UserMixin
from werkzeug.security import check_password_hash, generate_password_hash

from apps.app import db, login_manager


# Create User class inherited db.Model, added UserMixin
class User(db.Model, UserMixin):
    # Table Name
    __tablename__ = "users"
    # Column
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String, index=True)
    email = db.Column(db.String, unique=True, index=True)
    password_hash = db.Column(db.String)
    created_at = db.Column(db.DateTime, default=datetime.now)
    updated_at = db.Column(db.DateTime, default=datetime.now, onupdate=datetime.now)

    # Set relationship using backref
    user_images = db.relationship(
        "UserImage", backref="user", order_by="desc(UserImage.id)"
    )

    # Pass word property
    @property
    def password(self):
        raise AttributeError("読み取り付加")

    # Set Hashed password via Setter function
    @password.setter
    def password(self, password):
        self.password_hash = generate_password_hash(password)

    # Password check
    def verify_password(self, password):
        return check_password_hash(self.password_hash, password)

    # Password duplicate check
    def is_duplicate_email(self):
        return User.query.filter_by(email=self.email).first() is not None


# make a function to fetch login user information
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(user_id)
