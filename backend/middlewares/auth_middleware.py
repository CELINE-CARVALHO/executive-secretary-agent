from flask import request, jsonify
from utils.security import decode_jwt


def jwt_required(func):
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            return jsonify({"error": "Authorization required"}), 401

        token = auth_header.split(" ")[1]
        try:
            payload = decode_jwt(token)
            request.user_id = payload["user_id"]
        except Exception:
            return jsonify({"error": "Invalid or expired token"}), 401

        return func(*args, **kwargs)

    wrapper.__name__ = func.__name__
    return wrapper
