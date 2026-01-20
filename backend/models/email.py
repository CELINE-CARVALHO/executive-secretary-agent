from backend.database.db import db
from datetime import datetime


class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(db.Integer)

    # ✅ MUST EXIST + MUST BE NULLABLE
    gmail_message_id = db.Column(db.String, unique=True, nullable=True)

    sender = db.Column(db.String, nullable=False)
    subject = db.Column(db.String)
    body = db.Column(db.Text)

    ai_summary = db.Column(db.Text)
    urgency_level = db.Column(db.String)
    category = db.Column(db.String)

    received_at = db.Column(db.DateTime, default=datetime.utcnow)
