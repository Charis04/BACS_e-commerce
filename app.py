from shophive_packages import create_app

app = create_app(config_name="development")

if __name__ == "__main__":
    """
    Run the Flask application.
    """
    app.run(debug=True)
