from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from src.core.database import get_db
from src.application.uow.unit_of_work import UnitOfWork, get_uow
from src.presentation.schemas.auth_schema import UserRegister, UserLogin, UserResponse, TokenResponse
from src.application.services.auth_service import AuthService

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register", response_model=UserResponse, status_code=201)
def register(body: UserRegister, uow: UnitOfWork = Depends(get_uow)):
    try:
        with uow.begin() as db:
            service = AuthService(db)
            result = service.register(body.email, body.password, body.full_name)
            return result
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.post("/login", response_model=TokenResponse)
def login(body: UserLogin, db: Session = Depends(get_db)):
    try:
        service = AuthService(db)
        token = service.login(body.email, body.password)
        return {"access_token": token}
    except ValueError as e:
        raise HTTPException(status_code=401, detail=str(e))
