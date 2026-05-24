from sqlalchemy.orm import Session

from src.infrastructure.persistence.models import JobModel, TextResultModel
from src.infrastructure.persistence.repositories import SQLJobRepository
from src.infrastructure.metrics.collector import metrics


class JobService:
    def __init__(self, db: Session):
        self._repo = SQLJobRepository(db)
        self._db = db

    def create_job(self, user_id: int, input_text: str) -> dict:
        job = self._repo.create(user_id, input_text)
        metrics.increment("jobs_created")
        return {"id": job.id, "status": job.status, "input_text": job.input_text}

    def get_job(self, job_id: int) -> dict | None:
        job = self._repo.find_by_id(job_id)
        if not job:
            return None
        return {"id": job.id, "status": job.status, "input_text": job.input_text}

    def list_user_jobs(self, user_id: int) -> list[dict]:
        jobs = self._repo.find_by_user(user_id)
        return [{"id": j.id, "status": j.status, "input_text": j.input_text} for j in jobs]


class ProcessTextService:
    def __init__(self, db: Session):
        self._db = db

    def process(self, job_id: int) -> dict:
        job = self._db.query(JobModel).filter(JobModel.id == job_id).first()
        if not job:
            raise ValueError("Job not found")

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
        job.status = "completed"
        self._db.flush()
        metrics.increment("texts_processed")

        return {
            "job_id": job_id,
            "word_count": word_count,
            "char_count": char_count,
            "processed_text": processed,
        }
