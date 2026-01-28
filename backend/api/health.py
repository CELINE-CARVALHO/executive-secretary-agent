from flask import Blueprint, jsonify, session
from datetime import datetime, timedelta

from backend.database.db import db
from backend.models.email import Email
from backend.models.user import User
from backend.models.task import Task
from backend.services.ai_email_service import AIEmailService
from backend.services.gmail_service import fetch_gmail_emails

emails_bp = Blueprint("emails", __name__)

# -----------------------------
# FALLBACK SUMMARY (GUARANTEED)
# -----------------------------
def fallback_summary(email: Email) -> str:
    if email.body and email.body.strip():
        return email.body.strip()[:200]
    if email.subject and email.subject.strip():
        return email.subject.strip()[:200]
    return "(No content)"


# -----------------------------
# GET EMAILS (AUTO SYNC + AI)
# -----------------------------
@emails_bp.route("", methods=["GET"])
def get_emails():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify([])

    user = User.query.get_or_404(user_id)

    new_emails = fetch_gmail_emails(user)

    for email in new_emails:
        try:
            AIEmailService.process_email(email)
        except Exception as e:
            email.ai_summary = fallback_summary(email)
            email.urgency_level = "low"
            email.category = "info"
            print("AI fallback used:", e)
        finally:
            email.processing_status = "completed"

    db.session.commit()

    emails = (
        Email.query
        .filter_by(user_id=user.id)
        .order_by(Email.received_at.desc())
        .all()
    )

    return jsonify([email.to_dict() for email in emails])


# -----------------------------
# MANUAL GMAIL SYNC
# -----------------------------
@emails_bp.route("/sync", methods=["POST"])
def sync_emails():
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    user = User.query.get_or_404(user_id)

    new_emails = fetch_gmail_emails(user)

    processed = 0
    fallback = 0

    for email in new_emails:
        try:
            db.session.add(email)
            AIEmailService.process_email(email)
            processed += 1
        except Exception as e:
            email.ai_summary = fallback_summary(email)
            email.urgency_level = "low"
            email.category = "info"
            fallback += 1
            print("AI fallback used:", e)
        finally:
            email.processing_status = "completed"

    db.session.commit()

    return jsonify({
        "status": "synced",
        "new_emails": len(new_emails),
        "ai_processed": processed,
        "fallback_used": fallback
    })


# -----------------------------
# PROCESS SINGLE EMAIL
# -----------------------------
@emails_bp.route("/<int:email_id>/process", methods=["POST"])
def process_single_email(email_id):
    email = Email.query.get_or_404(email_id)

    try:
        AIEmailService.process_email(email)
    except Exception as e:
        email.ai_summary = fallback_summary(email)
        email.urgency_level = "low"
        email.category = "info"
        print("AI fallback used:", e)
    finally:
        email.processing_status = "completed"
        email.processed_at = datetime.utcnow()
        db.session.commit()

    return jsonify(email.to_dict())


# -----------------------------
# APPROVE EMAIL → TASK + CALENDAR
# -----------------------------
@emails_bp.route("/<int:email_id>/approve", methods=["POST"])
def approve_email(email_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    email = Email.query.get_or_404(email_id)
    user = User.query.get_or_404(user_id)

    if not email.ai_summary:
        try:
            AIEmailService.process_email(email)
        except Exception:
            email.ai_summary = fallback_summary(email)
            email.urgency_level = "low"
            email.category = "info"
        finally:
            email.processing_status = "completed"

    task = Task(
        user_id=user.id,
        email_id=email.id,
        title=email.ai_summary or email.subject,
        description=email.body,
        priority=email.urgency_level or "medium",
        suggested_deadline=email.ai_deadline or (datetime.utcnow() + timedelta(hours=2)),
        status="pending"
    )

    db.session.add(task)
    db.session.flush()

    from backend.services.calendar_service import create_calendar_event
    create_calendar_event(user, task)

    email.decision_status = "approved"
    email.decision_at = datetime.utcnow()

    db.session.commit()

    return jsonify({"success": True})


# -----------------------------
# REJECT EMAIL
# -----------------------------
@emails_bp.route("/<int:email_id>/reject", methods=["POST"])
def reject_email(email_id):
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"error": "unauthorized"}), 401

    email = Email.query.get_or_404(email_id)
    db.session.delete(email)
    db.session.commit()

    return jsonify({"status": "deleted"})
