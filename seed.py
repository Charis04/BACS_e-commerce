from shophive_packages import create_app, db
from shophive_packages.models import (
    User,
    Product,
    Order,
    Seller,
    OrderItem,
    Tag,
    Category,
    Cart,
)

app = create_app()

# Create an application context
with app.app_context():
    """
    Seed the database with sample data.

    This script creates sample users and products, adds them to the session,
    and commits the session to the database.
    """

    # Create sample users
    user1 = User(username="john", email="john@example.com",
                 password="password123")
    user2 = Seller(username="jane", email="jane@example.com",
                   password="password456")

    # Create sample products
    product1 = Product(
        name="Laptop",
        description="A high-performance laptop.",
        price=999.99,
    )
    product2 = Product(
        name="Smartphone",
        description="A latest model smartphone.",
        price=799.99,
    )

    # Add the sample data to the session and commit
    db.session.add(user1)
    db.session.add(user2)
    db.session.add(product1)
    db.session.add(product2)
    db.session.commit()

    order1 = Order(total_amount=3000, buyer_id=1)
    item1 = OrderItem(quantity=2, price=200, order_id=1, product_id=1,
                      seller_id=1)
    item2 = OrderItem(quantity=1, price=190, order_id=1, product_id=2,
                      seller_id=1)
    tag1 = Tag(name="Phone")
    cat1 = Category(name="Electronic")
    cart1 = Cart(user_id=1, quantity=2)
    p = Product(
        name="Louis V",
        description="Expensive LV shoe.",
        price=999.99,
        cart_id=1,
    )
    db.session.add_all([order1, item1, item2, tag1, cat1, cart1, p])
    db.session.commit()

    print("Database has been seeded with sample data.")
