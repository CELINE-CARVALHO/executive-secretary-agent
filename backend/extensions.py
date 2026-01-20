from flask_cors import CORS
from flask_jwt_extended import JWTManager
from backend.database.db import db


jwt = JWTManager()

def init_extensions(app):
    """
    Initialize Flask extensions
    """
    # Database
    db.init_app(app)

    # JWT
    jwt.init_app(app)

    # CORS
    CORS(app)
