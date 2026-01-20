from flask import Flask, request, jsonify
import json

from backend.config import config_by_name
from backend.extensions import init_extensions
from backend.api import register_blueprints
from backend.database.db import db
from backend.services.agent_orchestrator import AgentOrchestrator

# -----------------------------
# Import models so SQLAlchemy
# knows about them
# -----------------------------
from backend.models.user import User
from backend.models.email import Email
from backend.models.task import Task
from backend.models.approval import Approval
from backend.models.calendar_event import CalendarEvent
from backend.models.notification import Notification
from backend.models.ai_log import AILog


def create_app(env_name="development"):
    app = Flask(__name__)

    # -----------------------------
    # Load config
    # -----------------------------
    config_class = config_by_name.get(env_name)
    app.config.from_object(config_class)

    # -----------------------------
    # Initialize extensions
    # -----------------------------
    init_extensions(app)

    # -----------------------------
    # Register blueprints
    # -----------------------------
    register_blueprints(app)

    # -----------------------------
    # Initialize AI orchestrator
    # -----------------------------
    orchestrator = AgentOrchestrator()

    # -----------------------------
    # API: Process Email
    # -----------------------------
    @app.route("/api/process-email", methods=["POST"])
    def process_email():
        data = request.get_json(force=True)

        email_data = {
            "sender": data.get("sender"),
            "subject": data.get("subject"),
            "body": data.get("body"),
        }

        try:
            # -------------------------
            # Run AI Orchestrator
            # -------------------------
            result = orchestrator.process_email(email_data)

            # -------------------------
            # Normalize AI output
            # -------------------------
            email_summary = result.get("email_summary") or {}
            if not isinstance(email_summary, dict):
                email_summary = {}

            # -------------------------
            # Save Email (SAFE)
            # -------------------------
            email = Email(
                user_id=None,
                gmail_message_id=None,   # IMPORTANT: avoid NOT NULL error
                sender=email_data["sender"],
                subject=email_data["subject"],
                body=email_data["body"],
                ai_summary=json.dumps(email_summary),
                urgency_level=email_summary.get("urgency"),
                category=email_summary.get("category"),
            )

            db.session.add(email)
            db.session.flush()  # get email.id without commit

            # -------------------------
            # Save AI Log (SAFE)
            # -------------------------
            ai_log = AILog(
                user_id=None,
                agent_name="agent_orchestrator",
                input_data=email_data,
                output_data=result,
                success=True,
            )

            db.session.add(ai_log)
            db.session.commit()

            return jsonify({
                "success": True,
                "email_id": email.id,
                "ai_log_id": ai_log.id,
                "data": result
            }), 200

        except Exception as e:
            db.session.rollback()

            ai_log = AILog(
                user_id=None,
                agent_name="agent_orchestrator",
                input_data=email_data,
                output_data=None,
                success=False,
                error_message=str(e),
            )

            db.session.add(ai_log)
            db.session.commit()

            return jsonify({
                "success": False,
                "error": str(e)
            }), 500

    # -----------------------------
    # Create tables (TEMP)
    # -----------------------------
    with app.app_context():
        db.create_all()

    return app


if __name__ == "__main__":
    app = create_app()
    app.run(host="0.0.0.0", port=5000, debug=True)
