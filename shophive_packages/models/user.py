from werkzeug.security import generate_password_hash, check_password_hash
from shophive_packages import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)

    # Relationships
    orders = db.relationship('Order', back_populates='buyer', lazy='select')

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

    def __repr__(self):
        return f'<Seller {self.username} {self.email}>'

    # Set the password hash
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if the password matches
    def check_password(self, password):
        return check_password_hash(self.password, password)
