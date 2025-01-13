from shophive_packages import create_app
from flask import session
from flask.wrappers import Response as FlaskResponse

app = create_app()
app.debug = True  # Enable debug mode
app.secret_key = 'dev'  # Set a secret key for development


@app.before_request
def before_request() -> None:
    print(f"\n=== Before Request Session ===\n{dict(session)}\n")
    session.modified = False  # Reset the modified flag
    print(f"\n=== Before Request Session ===\n{dict(session)}\n")
    session.modified = False  # Reset the modified flag


@app.after_request
def after_request(response: FlaskResponse) -> FlaskResponse:
    if session.modified:
        print(f"\n=== After Request Session (Modified) ===\n{dict(session)}\n")
    return response


if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port=5000)
