from shophive_packages import db
# from datetime import datetime

# Add documentation

class Order(db.Model):
    
    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False)
    status = db.Column(
        db.Enum("Pending", "Processing", "Shipped", "Delivered", "Cancelled",
              name="order_status"),
        default="Pending")
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now())

    # Foreign keys
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    # item_id = db.Column(db.Integer, db.ForeignKey("product.id"), nullable=False)
    #seller_id = db.Column(
    #   db.Integer, db.ForeignKey("seller.id"), nullable=False)

    # Relationships

    buyer = db.relationship("User", back_populates="orders")
    # seller = db.relationship("Seller", backref="order", lazy=True)
    # items = db.relationship(
    #    "Product", backref="order", lazy=True)
    # history = db.relationship(
    # "OrderHistory", back_populates="order", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<Order {self.id} {self.status}>"
