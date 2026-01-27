from flask import Blueprint, request, jsonify
import logging
from backend.services.task_service import TaskService

logger = logging.getLogger(__name__)

approvals_bp = Blueprint("approvals", __name__, url_prefix="/api/approvals")
task_service = TaskService()


@approvals_bp.route("/<int:approval_id>/approve", methods=["POST"])
def approve_task(approval_id):
    data = request.json or {}
    approval = task_service.approve(
        approval_id,
        user_id=data["user_id"],
        modified_data=data.get("modified_data")
    )
    return jsonify({"status": approval.status}), 200


@approvals_bp.route("/<int:approval_id>/reject", methods=["POST"])
def reject_task(approval_id):
    data = request.json or {}
    approval = task_service.reject(
        approval_id,
        user_id=data["user_id"],
        feedback=data.get("feedback")
    )
    return jsonify({"status": approval.status}), 200
