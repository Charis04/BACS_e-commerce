from flask import request, jsonify, render_template
from shophive_packages import db, app
from shophive_packages.models import Order, OrderItem, Product



@app.route('/', methods=['GET'], strict_slashes=False)
@app.route('/home', methods=['GET'], strict_slashes=False)
def home():
    product = Product.query.all()

    return render_template('home.html', products=product)
