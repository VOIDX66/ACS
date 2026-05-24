from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    DATABASE_URL: str = "postgresql://acs_user:acs_pass@localhost:5432/acs_payments"
    SECRET_KEY: str = "dev-secret-key"
    API_HOST: str = "0.0.0.0"
    API_PORT: int = 8000
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

    QUEUE_MAX_SIZE: int = 20
    PAYMENT_WORKERS: int = 3
    COMMISSION_RATE: float = 0.05

    model_config = {"env_file": ".env"}


settings = Settings()
