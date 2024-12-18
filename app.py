from flask import Flask
from flask_jwt_extended import JWTManager
from shophive_packages import db
from flask_migrate import Migrate
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = os.getenv('SECRET_KEY')  # Add JWT_SECRET_KEY

db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Register routes
from shophive_packages.routes.user_routes import *

if __name__ == '__main__':
    app.run(debug=True)
