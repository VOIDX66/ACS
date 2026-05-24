from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.presentation.api.deps import get_current_user
from src.presentation.schemas.job_schema import JobCreate, JobResponse, JobResultResponse
from src.infrastructure.persistence.models import UserModel
from src.application.services.job_service import JobService, ProcessTextService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    body: JobCreate,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = JobService(db)
    return service.create_job(user.id, body.input_text)


@router.get("/", response_model=list[JobResponse])
def list_jobs(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = JobService(db)
    return service.list_user_jobs(user.id)


@router.get("/{job_id}", response_model=JobResponse)
def get_job(
    job_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = JobService(db)
    result = service.get_job(job_id)
    if not result:
        raise HTTPException(status_code=404, detail="Job not found")
    return result


@router.post("/{job_id}/process", response_model=JobResultResponse)
def process_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = ProcessTextService(db)
    try:
        return service.process(job_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
