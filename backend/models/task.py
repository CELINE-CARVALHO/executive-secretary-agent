from backend.database.db import db
from datetime import datetime

class Task(db.Model):
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True)
    email_id = db.Column(db.Integer, db.ForeignKey("emails.id"))
    user_id = db.Column(db.Integer, db.ForeignKey("users.id"))
    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)
    priority = db.Column(db.String, default="medium")
    status = db.Column(db.String, default="pending_approval")
    estimated_duration = db.Column(db.Integer)
    suggested_deadline = db.Column(db.DateTime)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
