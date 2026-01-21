from flask_sqlalchemy import SQLAlchemy
from backend.logger import setup_logging

logger = setup_logging()

db = SQLAlchemy()

logger.debug(f"[db.py] SQLAlchemy instance CREATED id={id(db)}")
