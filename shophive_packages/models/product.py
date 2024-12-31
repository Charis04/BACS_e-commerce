from shophive_packages import db
from sqlalchemy.sql import func
from shophive_packages.models.categories import product_categories
from shophive_packages.models.tags import product_tags


class Product(db.Model):
    __tablename__ = 'product'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.String(200), nullable=False)
    price = db.Column(db.Float(), nullable=False)
    image_url = db.Column(db.String(200), nullable=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())
    # establish relationship for Product-Category many to many relationship
    categories = db.relationship('Category', secondary='product_categories',
                                 backref=db.backref('product',
                                                    lazy='dynamic'))
    # establish arelationship for Product-Tag many to many relationship
    tags = db.relationship('Tag', secondary='product_tags',
                           backref=db.backref('product', lazy='dynamic'))
    # create sorting features for sales and stock available
    sales = db.Column(db.Integer, default=0)
    quantity = db.Column(db.Integer, default=0)

    def __repr__(self):
        return f'<Product {self.name}>'
