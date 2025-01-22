import unittest
from shophive_packages import create_app, db
from shophive_packages.models import Order, OrderItem, User, Product, Seller

class TestOrderModel(unittest.TestCase):

    def setUp(self):
        """Set up test variables and initialize app."""
        self.app = create_app('testing')
        self.app_context = self.app.app_context()
        self.app_context.push()
        db.create_all()

        # Create a test user
        self.user = User(username="testuser", email="test@example.com")
        self.user.set_password("password")
        db.session.add(self.user)
        db.session.commit()

        # Create a test seller
        self.seller = Seller(username="testseller", email="seller@example.com")
        self.seller.set_password("password")
        db.session.add(self.seller)
        db.session.commit()

        # Create a test product
        self.product = Product(name="Test Product", price=10.00)
        db.session.add(self.product)
        db.session.commit()

    def tearDown(self):
        """Tear down test variables."""
        db.session.remove()
        db.drop_all()
        self.app_context.pop()

    def test_order_creation(self):
        """Test order creation."""
        order = Order(buyer_id=self.user.id, total_amount=100.00)
        db.session.add(order)
        db.session.commit()

        self.assertEqual(Order.query.count(), 1)
        self.assertEqual(order.buyer_id, self.user.id)
        self.assertEqual(order.total_amount, 100.00)
        self.assertEqual(order.status, "Pending")

    def test_order_item_creation(self):
        """Test order item creation."""
        order = Order(buyer_id=self.user.id, total_amount=100.00)
        db.session.add(order)
        db.session.commit()

        order_item = OrderItem(
            order_id=order.id,
            product_id=self.product.id,
            quantity=2,
            price=20.00,
            seller_id=self.seller.id
        )
        db.session.add(order_item)
        db.session.commit()

        self.assertEqual(OrderItem.query.count(), 1)
        self.assertEqual(order_item.order_id, order.id)
        self.assertEqual(order_item.product_id, self.product.id)
        self.assertEqual(order_item.quantity, 2)
        self.assertEqual(order_item.price, 20.00)
        self.assertEqual(order_item.status, "Pending")

    def test_order_relationships(self):
        """Test order relationships."""
        order = Order(buyer_id=self.user.id, total_amount=100.00)
        db.session.add(order)
        db.session.commit()

        order_item = OrderItem(
            order_id=order.id,
            product_id=self.product.id,
            quantity=2,
            price=20.00,
            seller_id=self.seller.id
        )
        db.session.add(order_item)
        db.session.commit()

        self.assertEqual(order.items[0].id, order_item.id)
        self.assertEqual(order.buyer.id, self.user.id)
        self.assertEqual(order_item.order.id, order.id)
        self.assertEqual(order_item.item.id, self.product.id)
        self.assertEqual(order_item.seller.id, self.seller.id)

if __name__ == '__main__':
    unittest.main()