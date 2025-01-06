#!/usr/bin/python3
"""
This module contains the product tags model
"""
from shophive_packages import db

# establish association table for Product-Tag many to many relationship
product_tags = db.Table(
    'product_tags',  # Name of the association table
    db.Column('product_id', db.Integer, db.ForeignKey('product.id'),
              primary_key=True),
    db.Column('tag_id', db.Integer, db.ForeignKey('tags.id'),
              primary_key=True)
)


class Tag(db.Model):
    __tablename__ = 'tags'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False, unique=True)
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(
        db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    def __repr__(self):
        """
        Return a string representation of the tag
        """
        return f"<Tag {self.name}>"
