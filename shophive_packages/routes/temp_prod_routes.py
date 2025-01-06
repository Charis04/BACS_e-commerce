@app.route("/add-product", methods=["POST"], strict_slashes=False)
def add_product() -> tuple:
    """
    Add a new product to the database.

    Returns:
        tuple: A success message and the HTTP status code.
    """
    from shophive_packages.models import Product

    data = request.json
    new_product = Product(
        name=data["name"], description=data["description"], price=data["price"]
    )
    db.session.add(new_product)
    db.session.commit()
    return {"message": "Product added successfully!"}, 201


@app.route("/delete-product/<int:product_id>", methods=["DELETE"],
           strict_slashes=False)
def delete_product(product_id: int) -> tuple:
    """
    Delete a product from the database.

    Args:
        product_id (int): The ID of the product to delete.

    Returns:
        tuple: A success or error message and the HTTP status code.
    """
    from shophive_packages.models import Product

    product = Product.query.get(product_id)
    if not product:
        return {"message": "Product not found!"}, 404
    db.session.delete(product)
    db.session.commit()
    return {"message": "Product deleted!"}, 200


@app.route("/add-to-cart/<int:product_id>", strict_slashes=False)
@login_required
def add_to_cart(product_id: int) -> Tuple[dict, int]:
    """
    Add a product to the user's cart.

    Args:
        product_id (int): The ID of the product to add to the cart.

    Returns:
        tuple: A success message and the HTTP status code, or an error message
        if the product is not found.
    """
    from shophive_packages.models import Cart, Product

    product = Product.query.get(product_id)
    if not product:
        return {"message": "Product not found!"}, 404
    new_cart_item = Cart(user_id=current_user.id, product_id=product.id)
    db.session.add(new_cart_item)
    db.session.commit()
    return {"message": "Product added to cart!"}, 201
