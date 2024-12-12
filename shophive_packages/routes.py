from flask import render_template
from shophive_packages import app

@app.route("/", strict_slashes=False)
@app.route("/home", strict_slashes=False)
def home():
    return render_template('home.html')