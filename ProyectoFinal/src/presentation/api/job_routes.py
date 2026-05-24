from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.application.uow.unit_of_work import UnitOfWork, get_uow
from src.presentation.api.deps import get_current_user
from src.presentation.schemas.job_schema import (
    JobCreate,
    JobResponse,
    JobResultResponse,
    JobUpdatePriority,
)
from src.infrastructure.persistence.models import UserModel
from src.application.services.job_service import JobService, ProcessTextService
from src.application.services.notification_service import NotificationService

router = APIRouter(prefix="/jobs", tags=["jobs"])


@router.post("/", response_model=JobResponse, status_code=201)
def create_job(
    body: JobCreate,
    uow: UnitOfWork = Depends(get_uow),
    user: UserModel = Depends(get_current_user),
):
    with uow.begin() as db:
        service = JobService(db)
        result = service.create_job(user.id, body.input_text, body.priority)
        return result


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


@router.patch("/{job_id}/cancel", response_model=JobResponse)
def cancel_job(
    job_id: int,
    uow: UnitOfWork = Depends(get_uow),
    user: UserModel = Depends(get_current_user),
):
    with uow.begin() as db:
        service = JobService(db)
        if not service.cancel_job(job_id):
            raise HTTPException(status_code=409, detail="Job cannot be cancelled")
        return service.get_job(job_id)


@router.patch("/{job_id}/priority", response_model=JobResponse)
def update_priority(
    job_id: int,
    body: JobUpdatePriority,
    uow: UnitOfWork = Depends(get_uow),
    user: UserModel = Depends(get_current_user),
):
    with uow.begin() as db:
        service = JobService(db)
        result = service.update_priority(job_id, body.priority)
        if not result:
            raise HTTPException(status_code=404, detail="Job not found")
        return result


@router.post("/{job_id}/process", response_model=JobResultResponse)
def process_job(
    job_id: int,
    background_tasks: BackgroundTasks,
    uow: UnitOfWork = Depends(get_uow),
    user: UserModel = Depends(get_current_user),
):
    with uow.begin() as db:
        service = ProcessTextService(db)
        try:
            result, event = service.process(job_id)
        except ValueError as e:
            raise HTTPException(status_code=404, detail=str(e))

    background_tasks.add_task(NotificationService.notify_job_completed, event)
    return result
