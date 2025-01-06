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
    """

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    orders = db.relationship('Order', back_populates='buyer', lazy='select')
    carts = db.relationship('Cart', backref='buyer', lazy=True)

    def __repr__(self):
        return f'<User {self.username} {self.email}>'

    # Set the password hash
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if the password matches
    def check_password(self, password):
        return check_password_hash(self.password, password)


class Seller(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    orders = db.relationship(
        'OrderItem', back_populates='seller', lazy='select')

    def __repr__(self) -> str:
        """
        Returns a string representation of the user.

        Returns:
            str: A string representation of the user.
        """
        return f"<Seller {self.username} {self.email}>"

    def set_password(self, password):
        """
        Set the user's password to a hashed value.

        Args:
            password (str): The plain-text password.
        """
        self.password = generate_password_hash(password)

    def check_password(self, password):
        """
        Check if the provided password matches the stored hashed password.

        Args:
            password (str): The plain-text password to check.

        Returns:
            bool: True if the password matches, False otherwise.
        """
        return check_password_hash(self.password, password)
