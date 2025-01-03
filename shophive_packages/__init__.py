from flask_sqlalchemy import SQLAlchemy
from flask import Flask, render_template, request
from flask_jwt_extended import JWTManager
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from typing import Tuple
from flask_restful import Api
from config import config
from flask_login import (
    LoginManager,
    login_required,
    login_user,
    logout_user,
    current_user,
)


# load environment variables
load_dotenv()


app = Flask(__name__)


app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db' # os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'daskjfladjsfljadsfj' #os.getenv('SECRET_KEY')
app.config['JWT_SECRET_KEY'] = 'aklsdfjladjfjasdfj' #os.getenv('SECRET_KEY')  # Add JWT_SECRET_KEY

db = SQLAlchemy(app)
# db.init_app(app)
jwt = JWTManager(app)
#migrate = Migrate(app, db)

# Register routes
from shophive_packages.routes import user_routes, order_routes
from shophive_packages.routes.user_routes import user_bp
from shophive_packages.routes.cart_routes import CartResource
from shophive_packages.routes.product_management_routes.new_product_routes import new_product_bp
from shophive_packages.routes.product_management_routes.update_product_routes import update_product_bp
from shophive_packages.routes.product_management_routes.delete_product_routes import delete_product_bp
from shophive_packages.routes.product_management_routes.read_product_routes import read_product_bp
from shophive_packages.routes.product_management_routes.pagination_routes import pagination_bp

app.register_blueprint(new_product_bp)
app.register_blueprint(update_product_bp)
app.register_blueprint(delete_product_bp)
app.register_blueprint(pagination_bp)
app.register_blueprint(read_product_bp)
app.register_blueprint(user_bp)
