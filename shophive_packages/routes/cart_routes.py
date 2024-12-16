from flask import request, jsonify
from flask_restful import Resource
from shophive_packages import db
from shophive_packages.models.cart import Cart

class CartResource(Resource):
    """
    Resource for managing shopping cart items.
    """

    def get(self):
        """
        Fetch and return all cart items for the current user.
        
        Returns:
            JSON response with cart data.
        """
        # Fetch and return cart data
        pass

    def post(self):
        """
        Add a product to the cart.

        Returns:
            JSON response with a success message and status code 201.
        """
        data = request.get_json()
        new_cart_item = Cart(
            user_id=data['user_id'],
            product_id=data['product_id'],
            quantity=data['quantity']
        )
        db.session.add(new_cart_item)
        db.session.commit()
        return jsonify({'message': 'Product added to cart'}), 201

    def put(self, cart_item_id: int):
        """
        Update the quantity of an item in the cart.

        Args:
            cart_item_id (int): The ID of the cart item to update.

        Returns:
            JSON response with a success message.
        """
        data = request.get_json()
        cart_item = Cart.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        cart_item.quantity = data['quantity']
        db.session.commit()
        return jsonify({'message': 'Cart item updated'})

    def delete(self, cart_item_id: int):
        """
        Remove an item from the cart.

        Args:
            cart_item_id (int): The ID of the cart item to remove.

        Returns:
            Empty response with status code 204.
        """
        cart_item = Cart.query.get(cart_item_id)
        if not cart_item:
            return jsonify({'message': 'Cart item not found'}), 404
        db.session.delete(cart_item)
        db.session.commit()
        return '', 204
