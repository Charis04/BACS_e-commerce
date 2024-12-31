from shophive_packages import db

class Product(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False)

    # Foreign keys
    # order_id = db.Column(db.Integer, db.ForeignKey("order_item.id"), nullable=True)
    
    # Relationships
    orders = db.relationship('OrderItem', back_populates='item', lazy='select')


    def __repr__(self):
        return f'<Product {self.name} {self.price}>'
