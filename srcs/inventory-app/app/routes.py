from flask import Blueprint, jsonify, request

from app import db
from app.models import Movie

movies_bp = Blueprint("movies", __name__, url_prefix="/api/movies")


@movies_bp.route("", methods=["GET"])
def get_movies():
    title = request.args.get("title")
    query = Movie.query
    if title:
        query = query.filter(Movie.title.ilike(f"%{title}%"))
    movies = query.all()
    return jsonify([m.to_dict() for m in movies]), 200


@movies_bp.route("", methods=["POST"])
def create_movie():
    data = request.get_json(silent=True) or {}
    title = data.get("title")
    if not title:
        return jsonify({"error": "title is required"}), 400

    movie = Movie(title=title, description=data.get("description"))
    db.session.add(movie)
    db.session.commit()
    return jsonify(movie.to_dict()), 200


@movies_bp.route("", methods=["DELETE"])
def delete_all_movies():
    deleted = db.session.query(Movie).delete()
    db.session.commit()
    return jsonify({"deleted": deleted}), 200


@movies_bp.route("/<int:movie_id>", methods=["GET"])
def get_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "movie not found"}), 404
    return jsonify(movie.to_dict()), 200


@movies_bp.route("/<int:movie_id>", methods=["PUT"])
def update_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "movie not found"}), 404

    data = request.get_json(silent=True) or {}
    if "title" in data:
        movie.title = data["title"]
    if "description" in data:
        movie.description = data["description"]
    db.session.commit()
    return jsonify(movie.to_dict()), 200


@movies_bp.route("/<int:movie_id>", methods=["DELETE"])
def delete_movie(movie_id):
    movie = Movie.query.get(movie_id)
    if not movie:
        return jsonify({"error": "movie not found"}), 404

    db.session.delete(movie)
    db.session.commit()
    return jsonify({"deleted": movie_id}), 200
