from backend.database.db import db
from datetime import datetime


class Notification(db.Model):
    __tablename__ = "notifications"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    task_id = db.Column(db.Integer)

    notification_type = db.Column(db.String, nullable=False)
    title = db.Column(db.String, nullable=False)
    message = db.Column(db.Text, nullable=False)

    scheduled_at = db.Column(db.DateTime, nullable=False)
    sent_at = db.Column(db.DateTime)

    status = db.Column(db.String, default="pending")
    delivery_method = db.Column(db.String, default="email")

    created_at = db.Column(db.DateTime, default=datetime.utcnow)
