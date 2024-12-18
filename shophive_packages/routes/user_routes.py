from flask import request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from services.auth_service import register_user, login_user
from shophive_packages import app

# User Registration
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()
    try:
        user = register_user(data['username'], data['email'], data['password'])
        return jsonify({"message": f"User {user.username} created successfully!"}), 201
    except ValueError as e:
        return jsonify({"message": str(e)}), 400

# User Login
@app.route("/login", methods=["POST"])
def login():
    data = request.get_json()
    try:
        token = login_user(data['username'], data['password'])
        return jsonify({"access_token": token}), 200
    except ValueError as e:
        return jsonify({"message": str(e)}), 401

# User Profile
@app.route("/profile", methods=["GET"])
@jwt_required()
def profile():
    current_user_id = get_jwt_identity()
    user = User.query.get_or_404(current_user_id)
    return jsonify({
        "username": user.username,
        "email": user.email
    })
