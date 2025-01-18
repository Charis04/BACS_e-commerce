#!/usr/bin/python3
"""
This module contains a model for product categories in the catalog
"""
from shophive_packages import db


# Association table for the product and category
product_categories = db.Table(
    'product_categories',
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'),
              primary_key=True),
    db.Column('category_id', db.Integer, db.ForeignKey('categories.id'),
              primary_key=True))


class Category(db.Model):  # type: ignore
    """
    A model for product categories in the catalog
    """
    __tablename__ = 'categories'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self) -> str:
        """
        Return a string representation of the category
        """
        return f"<Category {self.name}>"
