from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from backend.models.email import Email
from backend.database.db import db
from datetime import datetime
import os
import base64
from bs4 import BeautifulSoup
import logging

logger = logging.getLogger(__name__)


def decode(data):
    if not data:
        return ""
    data += "=" * (-len(data) % 4)
    return base64.urlsafe_b64decode(data).decode("utf-8", errors="ignore")


def extract_body(payload):
    if payload.get("body", {}).get("data"):
        return decode(payload["body"]["data"])

    for part in payload.get("parts", []):
        mime = part.get("mimeType")
        data = part.get("body", {}).get("data")

        if mime == "text/plain" and data:
            return decode(data)

        if mime == "text/html" and data:
            return BeautifulSoup(decode(data), "html.parser").get_text(
                separator="\n", strip=True
            )

        if part.get("parts"):
            inner = extract_body(part)
            if inner:
                return inner

    return ""


def fetch_gmail_emails(user):
    if not user.gmail_token:
        logger.warning("No gmail token for user %s", user.id)
        return 0

    creds = Credentials(
        token=None,
        refresh_token=user.gmail_token,
        token_uri="https://oauth2.googleapis.com/token",
        client_id=os.getenv("GOOGLE_CLIENT_ID"),
        client_secret=os.getenv("GOOGLE_CLIENT_SECRET"),
        scopes=["https://www.googleapis.com/auth/gmail.readonly"],
    )

    service = build("gmail", "v1", credentials=creds)

    # 🔥 IMPORTANT: force multiple recent emails
    result = service.users().messages().list(
        userId="me",
        maxResults=20,
        includeSpamTrash=False,
    ).execute()

    messages = result.get("messages", [])
    logger.info("📬 Gmail returned %s messages", len(messages))

    created = 0

    for msg in messages:
        msg_id = msg["id"]

        if Email.query.filter_by(gmail_message_id=msg_id).first():
            continue

        full = service.users().messages().get(
            userId="me",
            id=msg_id,
            format="full"
        ).execute()

        headers = full.get("payload", {}).get("headers", [])

        def h(name):
            return next(
                (x["value"] for x in headers if x["name"].lower() == name.lower()),
                None
            )

        ts = int(full.get("internalDate", 0)) / 1000

        email = Email(
            user_id=user.id,
            gmail_message_id=msg_id,
            sender=h("From"),
            subject=h("Subject"),
            body=extract_body(full.get("payload", {})),
            received_at=datetime.utcfromtimestamp(ts),
            processing_status="pending",
        )

        db.session.add(email)
        created += 1

    db.session.commit()
    logger.info("✅ Gmail sync complete | new emails inserted=%s", created)
    return created
