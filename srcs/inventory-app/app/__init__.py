import os

from flask import Flask
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    db_user = os.environ["INVENTORY_DB_USER"]
    db_password = os.environ["INVENTORY_DB_PASSWORD"]
    db_host = os.environ["INVENTORY_DB_HOST"]
    db_port = os.environ.get("INVENTORY_DB_PORT", "5432")
    db_name = os.environ["INVENTORY_DB_NAME"]

    app.config["SQLALCHEMY_DATABASE_URI"] = (
        f"postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}"
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import movies_bp

    app.register_blueprint(movies_bp)

    with app.app_context():
        db.create_all()

    return app
