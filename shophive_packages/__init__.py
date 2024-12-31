from flask_sqlalchemy import SQLAlchemy
from flask import Flask
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os

app = Flask(__name__)

app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'daskjfladjsfljadsfj' #os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = 'aklsdfjladjfjasdfj' #os.getenv('SECRET_KEY')  # Add JWT_SECRET_KEY

db = SQLAlchemy(app)
# db.init_app(app)
jwt = JWTManager(app)
migrate = Migrate(app, db)

# Register routes
from shophive_packages.routes import user_routes, order_routes # Import failure due to route file


# Initialize the SQLAlchemy object

