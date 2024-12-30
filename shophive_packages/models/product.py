from shophive_packages import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    # order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    # order = db.relationship('Order', backref='item')

    def __repr__(self):
        return f'<Product {self.name} {self.price}>'
