from abc import ABC, abstractmethod

from src.domain.entities.payment_request import PaymentRequest


class UserRepository(ABC):
    @abstractmethod
    def find_by_email(self, email: str): ...

    @abstractmethod
    def create(self, email: str, hashed_password: str, full_name: str): ...


class JobRepository(ABC):
    @abstractmethod
    def create(self, user_id: int, input_text: str, priority: int = 0): ...

    @abstractmethod
    def find_by_id(self, job_id: int): ...

    @abstractmethod
    def find_by_user(self, user_id: int) -> list: ...

    @abstractmethod
    def update_status(self, job_id: int, status: str): ...

    @abstractmethod
    def cancel_job(self, job_id: int) -> bool: ...
