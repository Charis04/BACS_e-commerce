from flask import Flask
from shophive_packages import db
from flask_migrate import Migrate
import os
from flask_restful import Api

# Initialize Flask application
app: Flask = Flask(__name__)

# Configure SQLAlchemy database URI and settings
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Initialize the database and migration objects with the app
db.init_app(app)
migrate = Migrate(app, db)

# Debug: Print registered tables to ensure models are loaded correctly
with app.app_context():
    from shophive_packages.models import User, Product
    print(f"Registered tables: {db.metadata.tables.keys()}")

# Import and add your cart routes here
from shophive_packages.routes.cart_routes import CartResource

api: Api = Api(app)
api.add_resource(CartResource, '/cart', '/cart/<int:cart_item_id>')

if __name__ == '__main__':
    """
    Run the Flask application.

    The app will run in debug mode on the default Flask port (5000).
    """
    app.run(debug=True)
