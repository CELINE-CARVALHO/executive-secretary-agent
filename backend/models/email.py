"""
Email Model
"""
from backend.database.db import db
from datetime import datetime, timezone
import json


class Email(db.Model):
    __tablename__ = 'emails'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    gmail_message_id = db.Column(db.String(255), unique=True, nullable=True)
    thread_id = db.Column(db.String(255), nullable=True)

    sender = db.Column(db.String(255), nullable=False)
    subject = db.Column(db.Text, nullable=True)
    body = db.Column(db.Text, nullable=True)

    received_at = db.Column(
        db.DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc)
    )

    # AI processing lifecycle
    processing_status = db.Column(
        db.String(50),
        default='pending'
    )  # pending | processing | completed | failed

    processed_at = db.Column(db.DateTime, nullable=True)

    # -----------------------------
    # AI-GENERATED INTELLIGENCE
    # -----------------------------
    ai_summary = db.Column(db.Text, nullable=True)

    urgency_level = db.Column(
        db.String(20),
        nullable=True
    )  # low | medium | high

    category = db.Column(
        db.String(50),
        nullable=True
    )  # meeting / task / finance / academic / etc.

    ai_actions = db.Column(
        db.Text,
        nullable=True
    )  # Stored as JSON string

    ai_deadline = db.Column(
        db.DateTime,
        nullable=True
    )

    # -----------------------------
    # SERIALIZATION
    # -----------------------------
    def to_dict(self):
        return {
            'id': self.id,
            'sender': self.sender,
            'subject': self.subject,
            'body': self.body,
            'received_at': self.received_at.isoformat() if self.received_at else None,

            'processing_status': self.processing_status,
            'processed_at': self.processed_at.isoformat() if self.processed_at else None,

            'ai_summary': self.ai_summary,
            'urgency_level': self.urgency_level,
            'category': self.category,
            'ai_actions': self._parse_actions(),
            'ai_deadline': self.ai_deadline.isoformat() if self.ai_deadline else None
        }

    # -----------------------------
    # HELPERS
    # -----------------------------
    def _parse_actions(self):
        if not self.ai_actions:
            return []
        try:
            return json.loads(self.ai_actions)
        except Exception:
            return []
