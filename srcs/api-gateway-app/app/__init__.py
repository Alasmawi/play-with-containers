import logging
import os
from logging.handlers import RotatingFileHandler

from flask import Flask


def create_app():
    app = Flask(__name__)
    # The audit's curl examples use trailing slashes (/api/movies/); accept both forms.
    app.url_map.strict_slashes = False

    log_dir = os.environ.get("GATEWAY_LOG_DIR", "/var/log/api-gateway-app")
    os.makedirs(log_dir, exist_ok=True)
    handler = RotatingFileHandler(os.path.join(log_dir, "gateway.log"), maxBytes=1_000_000, backupCount=3)
    handler.setFormatter(logging.Formatter("%(asctime)s %(levelname)s %(message)s"))
    app.logger.addHandler(handler)
    app.logger.setLevel(logging.INFO)
    logging.getLogger("werkzeug").addHandler(handler)

    from app.routes import gateway_bp

    app.register_blueprint(gateway_bp)

    return app
