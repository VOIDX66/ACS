from sqlalchemy.orm import Session

from src.domain.events.job_completed import JobCompletedEvent
from src.infrastructure.persistence.models import JobModel, TextResultModel
from src.infrastructure.persistence.repositories import SQLJobRepository
from src.infrastructure.metrics.collector import metrics


class JobService:
    def __init__(self, db: Session):
        self._repo = SQLJobRepository(db)
        self._db = db

    def create_job(self, user_id: int, input_text: str, priority: int = 0) -> dict:
        job = self._repo.create(user_id, input_text, priority)
        metrics.increment("jobs_created")
        return {
            "id": job.id,
            "status": job.status,
            "priority": job.priority,
            "input_text": job.input_text,
        }

    def get_job(self, job_id: int) -> dict | None:
        job = self._repo.find_by_id(job_id)
        if not job:
            return None
        return {
            "id": job.id,
            "status": job.status,
            "priority": job.priority,
            "input_text": job.input_text,
        }

    def list_user_jobs(self, user_id: int) -> list[dict]:
        jobs = self._repo.find_by_user(user_id)
        return [
            {"id": j.id, "status": j.status, "priority": j.priority, "input_text": j.input_text}
            for j in jobs
        ]

    def cancel_job(self, job_id: int) -> bool:
        cancelled = self._repo.cancel_job(job_id)
        if cancelled:
            metrics.increment("jobs_cancelled")
        return cancelled

    def update_priority(self, job_id: int, priority: int) -> dict | None:
        job = self._db.query(JobModel).filter(JobModel.id == job_id).first()
        if not job:
            return None
        job.priority = priority
        self._db.flush()
        return {
            "id": job.id,
            "status": job.status,
            "priority": job.priority,
            "input_text": job.input_text,
        }


class ProcessTextService:
    def __init__(self, db: Session):
        self._db = db
        self._repo = SQLJobRepository(db)

    def process(self, job_id: int) -> tuple[dict, JobCompletedEvent]:
        job = self._repo.find_by_id(job_id)
        if not job:
            raise ValueError("Job not found")

        if job.status == "cancelled":
            raise ValueError("Cannot process a cancelled job")

        self._repo.update_status(job_id, "processing")

        text = job.input_text
        word_count = len(text.split())
        char_count = len(text)
        processed = text.upper()

        result = TextResultModel(
            job_id=job_id,
            word_count=word_count,
            char_count=char_count,
            processed_text=processed,
        )
        self._db.add(result)
        self._repo.update_status(job_id, "completed")
        metrics.increment("texts_processed")

        result_dict = {
            "job_id": job_id,
            "word_count": word_count,
            "char_count": char_count,
            "processed_text": processed,
        }

        event = JobCompletedEvent(
            job_id=job_id,
            user_id=job.user_id,
            result_summary=f"{word_count} words, {char_count} chars",
        )

        return result_dict, event
