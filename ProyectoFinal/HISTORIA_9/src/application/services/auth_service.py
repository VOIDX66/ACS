from sqlalchemy.orm import Session

from src.domain.value_objects.email import Email
from src.domain.value_objects.password import Password
from src.infrastructure.auth.jwt_handler import create_access_token, hash_password, verify_password
from src.infrastructure.persistence.repositories import SQLUserRepository


class AuthService:
    def __init__(self, db: Session):
        self._repo = SQLUserRepository(db)

    def register(self, email: str, password: str, full_name: str) -> dict:
        Email(email)
        Password.validate(password)

        existing = self._repo.find_by_email(email)
        if existing:
            raise ValueError("Email already registered")

        hashed = hash_password(password)
        user = self._repo.create(email=email, hashed_password=hashed, full_name=full_name)
        return {"id": user.id, "email": user.email, "full_name": user.full_name}

    def login(self, email: str, password: str) -> str:
        user = self._repo.find_by_email(email)
        if not user or not verify_password(password, user.hashed_password):
            raise ValueError("Invalid credentials")
        return create_access_token(user.id)
