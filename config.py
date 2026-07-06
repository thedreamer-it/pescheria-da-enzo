import os

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

class Config:
    SECRET_KEY = os.getenv("SECRET_KEY", "pescheria-secret-key")
    DB_ENGINE = os.getenv("DB_ENGINE", "sqlite")

    if DB_ENGINE == "postgres":
        PG_USER = os.getenv("PG_USER", "postgres")
        PG_PASSWORD = os.getenv("PG_PASSWORD", "postgres")
        PG_HOST = os.getenv("PG_HOST", "localhost")
        PG_PORT = os.getenv("PG_PORT", "5432")
        PG_DATABASE = os.getenv("PG_DATABASE", "pescheria_da_enzo")
        SQLALCHEMY_DATABASE_URI = f"postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DATABASE}"
    else:
        SQLALCHEMY_DATABASE_URI = "sqlite:///" + os.path.join(BASE_DIR, "instance", "pescheria.db")

    SQLALCHEMY_TRACK_MODIFICATIONS = False
