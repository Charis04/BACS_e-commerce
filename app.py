from shophive_packages import create_app, db  # noqa

app = create_app()

if __name__ == "__main__":
    app.run(debug=True)
