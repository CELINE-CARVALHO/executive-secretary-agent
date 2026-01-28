import os
import json
from datetime import datetime
from groq import Groq


class AIEmailService:
    MODEL = "llama-3.1-8b-instant"
    MAX_RETRIES = 2

    # 🔥 THE ONLY PUBLIC METHOD YOU EVER CALL
    @staticmethod
    def process_email(email):
        if not email.body:
            raise ValueError("Email body is empty")

        subject = email.subject or "(No Subject)"
        body = email.body.strip()

        result = AIEmailService._run_ai(subject, body)

        email.ai_summary = result["summary"]
        email.urgency_level = result["urgency"]
        email.category = result["category"]
        email.ai_actions = json.dumps(result["actions"])
        email.ai_deadline = result["deadline"]

    # -----------------------------
    # INTERNAL AI CALL
    # -----------------------------
    @classmethod
    def _run_ai(cls, subject: str, body: str) -> dict:
        prompt = cls._build_prompt(subject, body)
        client = cls._get_client()

        for _ in range(cls.MAX_RETRIES):
            response = cls._call_llm(client, prompt)
            parsed = cls._parse_response(response)
            if parsed:
                return parsed

        raise ValueError("AI failed to return valid structured JSON")

    @staticmethod
    def _get_client():
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise RuntimeError("GROQ_API_KEY not set")
        return Groq(api_key=api_key)

    # -----------------------------
    # PROMPT
    # -----------------------------
    @staticmethod
    def _build_prompt(subject: str, body: str) -> str:
        return f"""
You are an executive email intelligence system.

STRICT RULES:
- Output ONLY valid JSON
- No markdown
- No explanations
- Always return all fields
- If the email is one line, summary MUST repeat it

Return EXACTLY this JSON:

{{
  "summary": "string",
  "urgency": "low|medium|high",
  "category": "meeting|task|academic|finance|personal|info|spam",
  "actions": [],
  "deadline": null
}}

EMAIL SUBJECT:
{subject}

EMAIL BODY:
{body}
""".strip()

    # -----------------------------
    # LLM CALL
    # -----------------------------
    @staticmethod
    def _call_llm(client, prompt: str) -> str:
        completion = client.chat.completions.create(
            model=AIEmailService.MODEL,
            messages=[
                {"role": "system", "content": "Return JSON only."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.2
        )
        return completion.choices[0].message.content.strip()

    # -----------------------------
    # VALIDATION
    # -----------------------------
    @staticmethod
    def _parse_response(text: str):
        try:
            data = json.loads(text)
        except Exception:
            return None

        required = {"summary", "urgency", "category", "actions", "deadline"}
        if not required.issubset(data):
            return None

        if data["urgency"] not in {"low", "medium", "high"}:
            return None

        if not isinstance(data["actions"], list):
            return None

        if data["deadline"]:
            try:
                data["deadline"] = datetime.fromisoformat(data["deadline"])
            except Exception:
                data["deadline"] = None

        return data
