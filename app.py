from flask import Flask
from shophive_packages import db
from flask_migrate import Migrate
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)
migrate = Migrate(app, db)

# Debug registered tables
with app.app_context():
    from shophive_packages.models import User, Product
    print(f"Registered tables: {db.metadata.tables.keys()}")

if __name__ == '__main__':
    app.run(debug=True)
