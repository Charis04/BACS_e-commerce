from app import app
from flask import render_template
from flask import jsonify, request
from shophive_packages.models.product import Product
from shophive_packages import db


@app.route("/", strict_slashes=False)
@app.route("/home", strict_slashes=False)
def home():
    return render_template('home.html')


@app.route("/api/products", methods=['POST'], strict_slashes=False)
def add_product():
    """
    Api endpoint to add a product to the catalog
    It accepts product details via Json payload and saves them to the database
    """
    # Parse the json payload
    data = request.get_json()
    # Check if the payload is empty
    if not data:
        return jsonify({"message": "No input data provided"}), 400

    name = data.get('name')
    description = data.get('description')
    price = data.get('price')

    # Validating the data
    if not name or not description or not price:
        return jsonify({"message": "Missing required fields"}), 400

    if not isinstance(price, (int, float)) or price <= 0:
        return jsonify({"message": "Price must be a positive number"}), 400

    # Creating the new product instance
    new_product = Product(name=name, description=description, price=price)

    # Adding the new product to the database
    try:
        db.session.add(new_product)
        db.session.commit()
        return jsonify(
            {
                "message": "Product added successfully",
                "product": {
                    "id": new_product.id,
                    "name": new_product.name,
                    "description": new_product.description,
                    "price": new_product.price
                }
            }), 201
    except Exception as e:
        db.session.rollback()  # reverse the transaction if an error occurs
        # Return an internal server error
        return jsonify({"message": str(e)}), 500
