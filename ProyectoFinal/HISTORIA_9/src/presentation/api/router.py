from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from src.core.database import engine, Base
from src.core.console import console
from src.presentation.api.auth_routes import router as auth_router
from src.presentation.api.job_routes import router as job_router
from src.presentation.api.payment_routes import router as payment_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="ACS Payment Engine",
        description="Concurrent distributed system for background task processing",
        version="1.0.0",
    )

    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    app.include_router(auth_router)
    app.include_router(job_router)
    app.include_router(payment_router)

    @app.on_event("startup")
    def on_startup():
        console.rule("[header]ACS Payment Engine[/]")
        console.log("[success]Creando tablas en PostgreSQL...[/]")
        Base.metadata.create_all(bind=engine)
        console.log("[success]Tablas creadas. Sistema listo.[/]")

    @app.get("/health")
    def health():
        return {"status": "ok"}

    return app


app = create_app()
