from shophive_packages import db

# Add documentation


class Order(db.Model):  # type: ignore[name-defined]

    id = db.Column(db.Integer, primary_key=True)
    total_amount = db.Column(db.Numeric(10, 2), nullable=False, default=0.0)
    status = db.Column(
        db.Enum(
            "Pending",
            "Processing",
            "Shipped",
            "Delivered",
            "Cancelled",
            name="order_status",
        ),
        default="Pending",
    )
    created_at = db.Column(db.DateTime, default=db.func.now())
    updated_at = db.Column(
        db.DateTime, default=db.func.now(), onupdate=db.func.now()
    )

    # Foreign keys
    buyer_id = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)

    # Relationships
    buyer = db.relationship("User", back_populates="orders")
    items = db.relationship("OrderItem", back_populates="order", lazy="select")
    # history = db.relationship(
    # "OrderHistory", back_populates="order", cascade="all, delete-orphan")

    def add_item(self, item: "OrderItem", address) -> None:
        if not self.id:
            db.session.add(self)
            db.session.commit()
        order_item = OrderItem(
                product_id=item.product_id,
                quantity=item.quantity,
                price=item.product.price,
                address=address,
                order_id=self.id,
                seller_id=item.product.seller_id
            )
        if not self.total_amount:
            self.total_amount = item.product.price * item.quantity
        self.total_amount += item.product.price * item.quantity
        db.session.add(order_item)
        db.session.commit()

    def __repr__(self) -> str:
        return f"<Order {self.id} {self.status}>"


class OrderItem(db.Model):  # type: ignore[name-defined]
    __tablename__ = "order_items"

    id = db.Column(db.Integer, primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)
    price = db.Column(db.Numeric(10, 2), nullable=False)
    address = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.Enum(
            "Pending",
            "Processing",
            "Shipped",
            "Delivered",
            "Cancelled",
            name="order_status",
        ),
        default="Pending",
    )

    # Foreign Keys
    order_id = db.Column(db.Integer, db.ForeignKey("order.id"), nullable=False)
    product_id = db.Column(
        db.Integer, db.ForeignKey("product.id"), nullable=False
    )
    seller_id = db.Column(
        db.Integer, db.ForeignKey("seller.id"), nullable=False
    )

    # Relationships
    order = db.relationship("Order", back_populates="items")
    item = db.relationship("Product", back_populates="orders")
    seller = db.relationship("Seller", back_populates="orders")

    def __repr__(self) -> str:
        return f"<Order_item ({self.id} {self.price} {self.quantity})>"


"""
class OrderHistory(db.Model):
    # Tracks changes in order status:
    __tablename__ = "order_history"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), nullable=False
    )
    status = db.Column(
        db.Enum(
            "Pending",
            "Processing",
            "Shipped",
            "Delivered",
            "Cancelled",
            name="order_status"
        )
    )
    timestamp = db.Column(db.DateTime, default=db.func.now())

    order = db.relationship("Order", back_populates="history")


class RefundRequest(db.Model):
    # Handles refund or return requests:
    __tablename__ = "refund_requests"

    id = db.Column(db.Integer, primary_key=True)
    order_id = db.Column(
        db.Integer, db.ForeignKey("orders.id"), nullable=False
    )
    reason = db.Column(db.String(255), nullable=False)
    status = db.Column(
        db.Enum("Pending", "Approved", "Rejected", name="refund_status"),
        default="Pending"
    )
    created_at = db.Column(db.DateTime, default=db.func.now())

    order = db.relationship("Order")
"""
