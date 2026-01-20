from google.oauth2 import id_token
from google.auth.transport import requests
from backend.models.user import User
from backend.database.db import db
from backend.utils.security import generate_jwt
from flask import current_app


def authenticate_google_user(id_token_str):
    try:
        idinfo = id_token.verify_oauth2_token(
            id_token_str,
            requests.Request(),
            current_app.config["GOOGLE_CLIENT_ID"],
        )

        google_id = idinfo["sub"]
        email = idinfo["email"]
        name = idinfo.get("name", "")

        user = User.query.filter_by(google_id=google_id).first()

        if not user:
            user = User(
                google_id=google_id,
                email=email,
                name=name,
            )
            db.session.add(user)
            db.session.commit()

        jwt_token = generate_jwt(user.id)

        return {
            "token": jwt_token,
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
            },
        }

    except Exception as e:
        raise ValueError("Invalid Google token") from e
