from backend.database.db import db
from datetime import datetime


class Email(db.Model):
    __tablename__ = "emails"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"), nullable=False)

    gmail_message_id = db.Column(db.String(255), unique=True, index=True)

    sender = db.Column(db.String(255))
    subject = db.Column(db.Text)
    body = db.Column(db.Text)

    received_at = db.Column(db.DateTime)
    processed_at = db.Column(db.DateTime)
    processing_status = db.Column(db.String(50), default="pending")

    ai_summary = db.Column(db.Text)
    urgency_level = db.Column(db.String(50))
    category = db.Column(db.String(100))
    ai_actions = db.Column(db.Text)
    ai_deadline = db.Column(db.DateTime)

    decision_status = db.Column(db.String(20), default="pending")
    decision_at = db.Column(db.DateTime)

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "subject": self.subject,
            "body": self.body,
            "received_at": self.received_at.isoformat() if self.received_at else None,
            "processing_status": self.processing_status,
            "ai_summary": self.ai_summary,
            "urgency_level": self.urgency_level,
            "category": self.category,
            "decision_status": self.decision_status,
        }
