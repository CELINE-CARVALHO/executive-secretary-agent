"""
Flask Extensions
"""
from flask_cors import CORS
from flask_migrate import Migrate

from backend.database.db import db
from backend.logger import setup_logging

logger = setup_logging()

cors = CORS()
migrate = Migrate()


def init_extensions(app):
    """
    Initialize Flask extensions.
    This MUST be called exactly once per app.
    """
    logger.debug(f"[extensions.py] init_extensions called | app id={id(app)}")

    # SQLAlchemy
    db.init_app(app)
    logger.debug(f"[extensions.py] db.init_app completed | db id={id(db)}")

    # CORS
    cors.init_app(
        app,
        resources={
            r"/api/*": {
                "origins": "*",
                "supports_credentials": True
            }
        }
    )
    logger.debug("[extensions.py] CORS initialized")

    # Migrations
    migrate.init_app(app, db)
    logger.debug("[extensions.py] Flask-Migrate initialized")
