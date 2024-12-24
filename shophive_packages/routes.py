from flask import render_template
from . import app


@app.route("/", strict_slashes=False)
@app.route("/home", strict_slashes=False)
def home():
    return render_template("home.html")
