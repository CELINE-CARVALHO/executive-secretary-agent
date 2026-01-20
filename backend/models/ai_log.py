from backend.database.db import db
from datetime import datetime
import json


class AILog(db.Model):
    __tablename__ = "ai_logs"

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer)

    agent_name = db.Column(db.String, nullable=False)

    input_data = db.Column(db.Text, nullable=False)
    output_data = db.Column(db.Text)

    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text)

    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def __init__(self, **kwargs):
        if "input_data" in kwargs:
            kwargs["input_data"] = json.dumps(kwargs["input_data"])
        if "output_data" in kwargs:
            kwargs["output_data"] = json.dumps(kwargs["output_data"])
        super().__init__(**kwargs)
