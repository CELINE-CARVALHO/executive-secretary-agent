from backend.database.db import db
from datetime import datetime


class CalendarEvent(db.Model):
    __tablename__ = "calendar_events"

    id = db.Column(db.Integer, primary_key=True)
    task_id = db.Column(db.Integer)
    user_id = db.Column(db.Integer, nullable=False)

    google_event_id = db.Column(db.String, unique=True)

    title = db.Column(db.String, nullable=False)
    description = db.Column(db.Text)

    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    location = db.Column(db.String)
    attendees = db.Column(db.Text)  # JSON string

    reminder_minutes = db.Column(db.Integer, default=15)
    created_by_agent = db.Column(db.Boolean, default=True)

    sync_status = db.Column(db.String, default="pending")
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
