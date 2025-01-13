from flask_login import UserMixin
from werkzeug.security import generate_password_hash, check_password_hash
from shophive_packages import db

class User(UserMixin, db.Model):
    """
    Represents a user in the system.

    Attributes:
        id (int): The unique identifier for the user.
        username (str): The username of the user.
        email (str): The email address of the user.
        password (str): The password of the user.
        role (str): The role of the user ("buyer" or "seller").
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)
    role = db.Column(db.String(10), nullable=False, default="buyer")

    # Relationships
    orders = db.relationship('Order', back_populates='buyer', lazy='select')
    products = db.relationship('Product', backref='seller', lazy=True)

    def __repr__(self):
        return f'<User {self.username} {self.role}>'

    # Set the password hash
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if the password matches
    def check_password(self, password):
        return check_password_hash(self.password, password)
