from contextlib import contextmanager

from sqlalchemy.orm import Session

from src.core.database import SessionLocal


class UnitOfWork:
    def __init__(self):
        self._session: Session | None = None

    def __enter__(self) -> Session:
        self._session = SessionLocal()
        return self._session

    def __exit__(self, exc_type, exc_val, exc_tb):
        if self._session is None:
            return
        try:
            if exc_type is not None:
                self._session.rollback()
            else:
                self._session.commit()
        finally:
            self._session.close()

    @contextmanager
    def begin(self):
        session = SessionLocal()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()
