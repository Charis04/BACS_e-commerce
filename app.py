from flask import session, Response, has_request_context
from shophive_packages import create_app

app = create_app()
app.debug = True


@app.before_request
def before_request() -> None:
    """Initialize cart session data only if it doesn't exist"""
    if has_request_context() and "cart_items" not in session:
        session["cart_items"] = []
        session["cart_total"] = 0.0
        session.modified = True
        print(f"\n=== Initialized new session ===\n{dict(session)}\n")


@app.after_request
def after_request(response: Response) -> Response:
    """Log session modifications"""
    if session.modified:
        print(f"\n=== After Request Session (Modified) ===\n{dict(session)}\n")
    return response


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
