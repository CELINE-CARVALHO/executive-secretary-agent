from flask import Blueprint, jsonify, session
from backend.models.email import Email
from backend.models.user import User
from backend.services.gmail_service import fetch_gmail_emails
import logging

emails_bp = Blueprint("emails", __name__)
logger = logging.getLogger(__name__)


@emails_bp.route("", methods=["GET"])
def get_emails():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([]), 200

    user = User.query.get(user_id)
    if not user:
        return jsonify([]), 200

    # 🔥 AUTO SYNC GMAIL
    try:
        created = fetch_gmail_emails(user)
        logger.info("📬 Auto Gmail sync ran | new=%s", created)
    except Exception:
        logger.exception("❌ Gmail sync failed")

    emails = (
        Email.query
        .filter_by(user_id=user.id)
        .order_by(Email.received_at.desc(), Email.id.desc())
        .all()
    )

    return jsonify([e.to_dict() for e in emails]), 200
