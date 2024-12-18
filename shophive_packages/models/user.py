from werkzeug.security import generate_password_hash, check_password_hash
from shophive_packages import db

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)  
    password = db.Column(db.String(200), nullable=False)

    def __repr__(self):
        return f'<User {self.username}>'

    # Set the password hash
    def set_password(self, password):
        self.password = generate_password_hash(password)

    # Check if the password matches
    def check_password(self, password):
        return check_password_hash(self.password, password)
