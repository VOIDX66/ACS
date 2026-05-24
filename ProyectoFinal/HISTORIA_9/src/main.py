import uvicorn

from src.presentation.api.router import app
from src.core.config import settings

if __name__ == "__main__":
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
