"""
AI Log Model
"""
from backend.database.db import db
from datetime import datetime
import json


class AILog(db.Model):
    __tablename__ = 'ai_logs'
    
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)
    
    agent_name = db.Column(db.String(100), nullable=False)
    
    input_data = db.Column(db.Text, nullable=True)
    output_data = db.Column(db.Text, nullable=True)
    prompt_used = db.Column(db.Text, nullable=True)
    
    model_used = db.Column(db.String(100), default='llama-3.3-70b-versatile')
    tokens_used = db.Column(db.Integer, nullable=True)
    latency_ms = db.Column(db.Integer, nullable=True)
    confidence_score = db.Column(db.Float, nullable=True)
    
    success = db.Column(db.Boolean, default=True)
    error_message = db.Column(db.Text, nullable=True)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    def __init__(self, **kwargs):
        """Initialize AILog with automatic JSON serialization"""
        # Handle input_data
        if 'input_data' in kwargs and not isinstance(kwargs['input_data'], str):
            kwargs['input_data'] = json.dumps(kwargs['input_data'])
        
        # Handle output_data
        if 'output_data' in kwargs and kwargs['output_data'] is not None:
            if not isinstance(kwargs['output_data'], str):
                kwargs['output_data'] = json.dumps(kwargs['output_data'])
        
        super(AILog, self).__init__(**kwargs)