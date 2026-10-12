import os

from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL

db = SQLAlchemy()


def create_app():
    app = Flask(__name__)

    # The audit's curl examples use trailing slashes (/api/movies/); accept both forms.
    app.url_map.strict_slashes = False

    # URL.create escapes special characters in the password.
    app.config["SQLALCHEMY_DATABASE_URI"] = URL.create(
        "postgresql",
        username=os.environ["INVENTORY_DB_USER"],
        password=os.environ["INVENTORY_DB_PASSWORD"],
        host=os.environ["INVENTORY_DB_HOST"],
        port=int(os.environ.get("INVENTORY_DB_PORT", 5432)),
        database=os.environ["INVENTORY_DB_NAME"],
    )
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db.init_app(app)

    from app.routes import movies_bp

    app.register_blueprint(movies_bp)

    @app.get("/health")
    def health():
        return jsonify({"status": "ok"}), 200

    with app.app_context():
        db.create_all()

    return app
