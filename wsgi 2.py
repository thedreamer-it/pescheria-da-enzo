from app import create_app

app = create_app()

if __name__ == "__main__":
    # Useful for local testing: python wsgi.py
    app.run(host="0.0.0.0", port=8080)
