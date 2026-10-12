import os

import requests
from flask import Blueprint, Response, current_app, jsonify, request

from app.rabbitmq import publish_billing_message

gateway_bp = Blueprint("gateway", __name__)


def inventory_base_url():
    return os.environ.get("INVENTORY_API_URL", "http://localhost:8080")


def _proxy_to_inventory(path):
    url = f"{inventory_base_url()}{path}"
    try:
        resp = requests.request(
            method=request.method,
            url=url,
            params=request.args,
            json=request.get_json(silent=True),
            timeout=10,
        )
    except requests.RequestException as exc:
        current_app.logger.error("inventory-app unreachable: %s", exc)
        return jsonify({"error": "inventory service unavailable"}), 502
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))


@gateway_bp.route("/health")
def health():
    return jsonify({"status": "ok"}), 200


@gateway_bp.route("/api/movies", methods=["GET", "POST", "DELETE"])
def movies_collection():
    return _proxy_to_inventory("/api/movies")


@gateway_bp.route("/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"])
def movies_item(movie_id):
    return _proxy_to_inventory(f"/api/movies/{movie_id}")


@gateway_bp.route("/api/billing", methods=["POST"])
def billing():
    payload = request.get_json(silent=True)
    if not isinstance(payload, dict):
        return jsonify({"error": "body must be a JSON object"}), 400

    try:
        publish_billing_message(payload)
    except Exception as exc:
        current_app.logger.error("rabbit-queue unreachable: %s", exc)
        return jsonify({"error": "message broker unavailable"}), 502

    current_app.logger.info("billing message queued for user_id=%s", payload.get("user_id"))

    return jsonify({"message": "Message posted"}), 200
