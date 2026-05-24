from sqlalchemy.orm import Session
from sqlalchemy import func

from src.infrastructure.persistence.models import UserModel, JobModel, TextResultModel
from src.infrastructure.metrics.collector import metrics
from src.core.console import console


class ReportService:
    def __init__(self, db: Session):
        self._db = db

    def summary(self) -> dict:
        total_users = self._db.query(func.count(UserModel.id)).scalar() or 0

        total_jobs = self._db.query(func.count(JobModel.id)).scalar() or 0

        jobs_by_status = (
            self._db.query(JobModel.status, func.count(JobModel.id))
            .group_by(JobModel.status)
            .all()
        )
        status_breakdown = {status: count for status, count in jobs_by_status}

        completed_jobs = status_breakdown.get("completed", 0)
        cancelled_jobs = status_breakdown.get("cancelled", 0)
        pending_jobs = status_breakdown.get("pending", 0)
        processing_jobs = status_breakdown.get("processing", 0)

        total_results = self._db.query(func.count(TextResultModel.id)).scalar() or 0
        total_words = self._db.query(func.sum(TextResultModel.word_count)).scalar() or 0
        total_chars = self._db.query(func.sum(TextResultModel.char_count)).scalar() or 0

        sys_metrics = metrics.snapshot()

        console.log(
            f"[info]Report generado:[/] "
            f"users={total_users} jobs={total_jobs} completed={completed_jobs}"
        )

        return {
            "users": total_users,
            "jobs": {
                "total": total_jobs,
                "completed": completed_jobs,
                "cancelled": cancelled_jobs,
                "pending": pending_jobs,
                "processing": processing_jobs,
            },
            "text_processing": {
                "total_results": total_results,
                "total_words": total_words,
                "total_chars": total_chars,
            },
            "metrics": {
                "uptime_seconds": round(sys_metrics["uptime"], 1),
                "counters": sys_metrics["counters"],
            },
        }

    def user_report(self, user_id: int) -> dict:
        user = self._db.query(UserModel).filter(UserModel.id == user_id).first()
        if not user:
            raise ValueError("User not found")

        jobs = (
            self._db.query(JobModel)
            .filter(JobModel.user_id == user_id)
            .order_by(JobModel.priority.desc(), JobModel.created_at.desc())
            .all()
        )

        jobs_detail = []
        for j in jobs:
            result = (
                self._db.query(TextResultModel)
                .filter(TextResultModel.job_id == j.id)
                .first()
            )
            jobs_detail.append(
                {
                    "job_id": j.id,
                    "status": j.status,
                    "priority": j.priority,
                    "input_text": j.input_text[:100],
                    "word_count": result.word_count if result else 0,
                    "char_count": result.char_count if result else 0,
                    "created_at": j.created_at.isoformat() if j.created_at else None,
                }
            )

        return {
            "user_id": user.id,
            "email": user.email,
            "full_name": user.full_name,
            "total_jobs": len(jobs),
            "jobs": jobs_detail,
        }
