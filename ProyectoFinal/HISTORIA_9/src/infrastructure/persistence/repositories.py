from sqlalchemy.orm import Session

from src.domain.interfaces.repositories import UserRepository, JobRepository
from src.infrastructure.persistence.models import UserModel, JobModel


class SQLUserRepository(UserRepository):
    def __init__(self, db: Session):
        self._db = db

    def find_by_email(self, email: str):
        return self._db.query(UserModel).filter(UserModel.email == email).first()

    def create(self, email: str, hashed_password: str, full_name: str) -> UserModel:
        user = UserModel(email=email, hashed_password=hashed_password, full_name=full_name)
        self._db.add(user)
        self._db.flush()
        return user


class SQLJobRepository(JobRepository):
    def __init__(self, db: Session):
        self._db = db

    def create(self, user_id: int, input_text: str) -> JobModel:
        job = JobModel(user_id=user_id, input_text=input_text)
        self._db.add(job)
        self._db.flush()
        return job

    def find_by_id(self, job_id: int):
        return self._db.query(JobModel).filter(JobModel.id == job_id).first()

    def find_by_user(self, user_id: int) -> list:
        return self._db.query(JobModel).filter(JobModel.user_id == user_id).all()

    def update_status(self, job_id: int, status: str):
        self._db.query(JobModel).filter(JobModel.id == job_id).update({"status": status})
        self._db.flush()
