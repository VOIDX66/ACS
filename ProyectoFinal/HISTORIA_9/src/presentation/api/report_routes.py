from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.presentation.api.deps import get_current_user
from src.presentation.schemas.report_schema import ReportSummary, UserReportResponse
from src.infrastructure.persistence.models import UserModel
from src.application.services.report_service import ReportService

router = APIRouter(prefix="/reports", tags=["reports"])


@router.get("/summary", response_model=ReportSummary)
def system_summary(
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = ReportService(db)
    return service.summary()


@router.get("/user/{user_id}", response_model=UserReportResponse)
def user_report(
    user_id: int,
    db: Session = Depends(get_db),
    user: UserModel = Depends(get_current_user),
):
    service = ReportService(db)
    try:
        return service.user_report(user_id)
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
