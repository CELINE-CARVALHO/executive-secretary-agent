from flask import Blueprint, request, jsonify, redirect
from services.auth_service import authenticate_google_user
import requests
import os
from urllib.parse import urlencode
from flask import current_app

auth_bp = Blueprint("auth", __name__, url_prefix="/auth")


@auth_bp.route("/google", methods=["POST"])
def google_login_api():
    """
    API-based login (frontend sends id_token)
    """
    data = request.get_json()
    if not data or "id_token" not in data:
        return jsonify({"error": "Missing id_token"}), 400

    try:
        result = authenticate_google_user(data["id_token"])
        return jsonify(result), 200
    except ValueError:
        return jsonify({"error": "Invalid Google token"}), 401


@auth_bp.route("/google/login", methods=["GET"])
def google_login_redirect():
    """
    Backend-only login (redirect-based)
    """
    params = {
        "client_id": current_app.config["GOOGLE_CLIENT_ID"],
        "response_type": "code",
        "scope": "openid email profile",
        "redirect_uri": "http://localhost:5000/auth/google/callback",
        "access_type": "offline",
        "prompt": "consent",
    }

    google_auth_url = (
        "https://accounts.google.com/o/oauth2/v2/auth?"
        + urlencode(params)
    )

    return redirect(google_auth_url)


@auth_bp.route("/google/callback", methods=["GET"])
def google_callback():
    code = request.args.get("code")
    if not code:
        return jsonify({"error": "Missing authorization code"}), 400

    token_response = requests.post(
        "https://oauth2.googleapis.com/token",
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "code": code,
            "client_id": current_app.config["GOOGLE_CLIENT_ID"],
            "client_secret": current_app.config["GOOGLE_CLIENT_SECRET"],
            "redirect_uri": "http://localhost:5000/auth/google/callback",
            "grant_type": "authorization_code",
        },
    )

    token_json = token_response.json()

    # 🔍 DEBUG SAFETY (temporary)
    if "error" in token_json:
        return jsonify({
            "error": "Google token exchange failed",
            "details": token_json
        }), 401

    if "id_token" not in token_json:
        return jsonify({
            "error": "Failed to obtain id_token",
            "google_response": token_json
        }), 401

    try:
        result = authenticate_google_user(token_json["id_token"])
        return jsonify(result), 200
    except ValueError:
        return jsonify({"error": "Authentication failed"}), 401
