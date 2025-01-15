from shophive_packages import create_app, db
from shophive_packages.models import (
    User, Product, Order, Seller, OrderItem, Tag, Category, Cart
)

app = create_app()

with app.app_context():
    # Create seller
    seller1 = Seller(username="jane", email="jane@example.com")
    seller1.set_password("password456")
    db.session.add(seller1)
    db.session.commit()

    # Create buyer
    buyer1 = User(
        username="john",
        email="john@example.com",
        password="password123",
        role="buyer"
    )
    db.session.add(buyer1)
    db.session.commit()

    # Create products
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
    db.session.add_all([product1, product2])
    db.session.commit()  # Commit to get product IDs

    # Create order and related items
    order1 = Order(total_amount=3000, buyer_id=buyer1.id)
    db.session.add(order1)
    db.session.commit()  # Commit to get order ID

    # Now create order items with valid seller_id
    item1 = OrderItem(
        quantity=2,
        price=200,
        order_id=order1.id,
        product_id=product1.id,
        seller_id=seller1.id  # Use actual seller ID
    )
    item2 = OrderItem(
        quantity=1,
        price=190,
        order_id=order1.id,
        product_id=product2.id,
        seller_id=seller1.id  # Use actual seller ID
    )

    # Create tags and categories
    tag1 = Tag(name="Phone")
    cat1 = Category(name="Electronic")

    # Create cart item
    cart1 = Cart(
        user_id=buyer1.id,
        product_id=product1.id,
        quantity=2
    )

    # Add remaining items and commit
    db.session.add_all([item1, item2, tag1, cat1, cart1])
    db.session.commit()

    print("Database has been seeded with sample data.")
    print("If you need to reset the database:")
    print("1. Enter flask shell")
    print("2. Run: db.drop_all()")
    print("3. Exit and re-enter flask shell")
    print("4. Run: db.create_all()")
    print("5. Exit and run: python seed.py")
