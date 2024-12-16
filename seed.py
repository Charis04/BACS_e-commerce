from app import app, db
from shophive_packages.models import User, Product  # Import your models here

# Create an application context
with app.app_context():
    # Create sample users
    user1 = User(username="john", email="john@example.com", password="password123")
    user2 = User(username="jane", email="jane@example.com", password="password456")

    # Create sample products
    product1 = Product(name="Laptop", description="A high-performance laptop.", price=999.99)
    product2 = Product(name="Smartphone", description="A latest model smartphone.", price=799.99)

    # Add the sample data to the session and commit
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    print("Database has been seeded with sample data.")
