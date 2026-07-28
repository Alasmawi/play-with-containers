import os

import requests
from flask import Blueprint, Response, jsonify, request

from app.rabbitmq import publish_billing_message

gateway_bp = Blueprint("gateway", __name__)


def inventory_base_url():
    return os.environ.get("INVENTORY_API_URL", "http://localhost:8080")


def _proxy_to_inventory(path):
    url = f"{inventory_base_url()}{path}"
    resp = requests.request(
        method=request.method,
        url=url,
        params=request.args,
        json=request.get_json(silent=True),
        timeout=10,
    )
    return Response(resp.content, status=resp.status_code, content_type=resp.headers.get("Content-Type"))


@gateway_bp.route("/api/movies", methods=["GET", "POST", "DELETE"])
def movies_collection():
    return _proxy_to_inventory("/api/movies")


@gateway_bp.route("/api/movies/<int:movie_id>", methods=["GET", "PUT", "DELETE"])
def movies_item(movie_id):
    return _proxy_to_inventory(f"/api/movies/{movie_id}")


@gateway_bp.route("/api/billing", methods=["POST"])
def billing():
    payload = request.get_json(silent=True)
    if payload is None:
        return jsonify({"error": "invalid or missing JSON body"}), 400

    try:
        publish_billing_message(payload)
    except Exception as exc:
        return jsonify({"error": "failed to reach message broker", "detail": str(exc)}), 502

    return jsonify({"message": "Message posted"}), 202
