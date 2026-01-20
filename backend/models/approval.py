from backend.database.db import db
from datetime import datetime


class Approval(db.Model):
    __tablename__ = "approvals"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer, nullable=False)

    approval_type = db.Column(db.String, nullable=False)
    status = db.Column(db.String, default="pending")

    original_data = db.Column(db.Text)
    modified_data = db.Column(db.Text)
    user_feedback = db.Column(db.Text)

    decision_at = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
