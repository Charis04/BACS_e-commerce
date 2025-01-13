from shophive_packages import app, db


@app.route("/add-user/<username>/<email>", strict_slashes=False)
def add_user(username: str, email: str) -> str:
    """
    Add a new user to the database.

    Args:
        username (str): The username of the new user.
        email (str): The email of the new user.

    Returns:
        str: Success message.
    """
    from shophive_packages.models import User

    new_user = User(username=username, email=email, password="securepassword")
    db.session.add(new_user)
    db.session.commit()
    return f"User {username} added!"


@app.route("/get-users", strict_slashes=False)
def get_users() -> dict:
    """
    Retrieve all users from the database.

    Returns:
        dict: A dictionary of user IDs and usernames.
    """
    from shophive_packages.models import User

    users = User.query.all()
    return {user.id: user.username for user in users}
