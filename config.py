import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.environ.get("SECRET_KEY", "dev")
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    if os.environ.get("DATABASE_URL"):
        SQLALCHEMY_DATABASE_URI = os.environ.get("DATABASE_URL")
    elif os.environ.get("PG_HOST"):
        PG_USER = os.environ.get("PG_USER")
        PG_PASSWORD = os.environ.get("PG_PASSWORD")
        PG_HOST = os.environ.get("PG_HOST")
        PG_PORT = os.environ.get("PG_PORT", "5432")
        PG_DATABASE = os.environ.get("PG_DATABASE")
        SQLALCHEMY_DATABASE_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "pescheria.db")
