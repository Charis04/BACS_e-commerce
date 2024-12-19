from flask import Flask
from shophive_packages import db
from flask_migrate import Migrate
import os
from dotenv import load_dotenv
from product_management_routes.new_product_routes import new_product_bp

# load environment variables
load_dotenv()

app = Flask(__name__)
app.register_blueprint(new_product_bp)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Debug registered tables
with app.app_context():
    from shophive_packages.models import User, Product
    print(f"Registered tables: {db.metadata.tables.keys()}")


for rule in app.url_map.iter_rules():
    print(f"{rule} -> {rule.methods}")


if __name__ == '__main__':
    app.run(host="127.0.0.1", port=5003, debug=True)
