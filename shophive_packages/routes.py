from flask import render_template
from app import app


@app.route("/", strict_slashes=False)
@app.route("/home", strict_slashes=False)
def home():
    """
    Render the home page.

    Returns:
        HTML: Rendered home page template.
    """
    return render_template("home.html")
