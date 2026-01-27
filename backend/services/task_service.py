import json
from datetime import datetime
from backend.database.db import db
from backend.models.task import Task
from backend.models.approval import Approval


class TaskService:

    def create_pending_approval(self, email, tasks, ai_review):
        task_ids = []

        for t in tasks:
            task = Task(
                email_id=email["id"],
                title=t["title"],
                description=t.get("explanation"),
                priority=t.get("priority", "medium"),
                status="pending_approval",
                created_by_agent=True
            )
            db.session.add(task)
            db.session.flush()
            task_ids.append(task.id)

        approval = Approval(
            user_id=email["user_id"],
            task_id=task_ids[0],
            status="pending",
            original_data=json.dumps({
                "email": email,
                "tasks": tasks,
                "ai_review": ai_review
            }),
            created_at=datetime.utcnow()
        )

        db.session.add(approval)
        db.session.commit()
        return approval

    def approve(self, approval_id, user_id, modified_data=None):
        approval = Approval.query.get_or_404(approval_id)
        approval.status = "approved"
        approval.user_id = user_id
        approval.modified_data = json.dumps(modified_data) if modified_data else None
        approval.decision_at = datetime.utcnow()

        task = Task.query.get(approval.task_id)
        if task:
            task.status = "approved"

        db.session.commit()
        return approval

    def reject(self, approval_id, user_id, feedback=None):
        approval = Approval.query.get_or_404(approval_id)
        approval.status = "rejected"
        approval.user_id = user_id
        approval.user_feedback = feedback
        approval.decision_at = datetime.utcnow()

        task = Task.query.get(approval.task_id)
        if task:
            task.status = "rejected"

        db.session.commit()
        return approval
