import jwt
from datetime import datetime, timedelta
from flask import current_app


def generate_jwt(user_id):
    payload = {
        "user_id": user_id,
        "exp": datetime.utcnow()
        + timedelta(minutes=int(current_app.config.get("JWT_EXP_MINUTES", 60))),
        "iat": datetime.utcnow(),
    }
    return jwt.encode(
        payload,
        current_app.config["JWT_SECRET_KEY"],
        algorithm="HS256",
    )


def decode_jwt(token):
    return jwt.decode(
        token,
        current_app.config["JWT_SECRET_KEY"],
        algorithms=["HS256"],
    )
# thieresfsec