import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from app.config import settings
from app.db import Base, SessionLocal, engine
from app.routers import api_router
from app.seed import seed_demo
from app.services.inference import disagg_service

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)-7s %(name)s: %(message)s",
)
logger = logging.getLogger("nilm")


@asynccontextmanager
async def lifespan(_: FastAPI):
    Base.metadata.create_all(bind=engine)
    if settings.seed_demo:
        db = SessionLocal()
        try:
            seed_demo(db)
        finally:
            db.close()
    logger.info(
        "inference backend=%s version=%s appliances=%s",
        disagg_service.backend,
        disagg_service.version,
        disagg_service.status()["appliances"],
    )
    yield


app = FastAPI(
    title="Building-Level NILM System API",
    version="1.0.0",
    lifespan=lifespan,
)

origins = [o.strip() for o in settings.cors_origins.split(",") if o.strip()]
wildcard = origins == ["*"]
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"] if wildcard else origins,
    # Browsers reject "*" together with credentials, so only enable it for
    # explicit origins.
    allow_credentials=not wildcard,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger.exception("unhandled error on %s %s", request.method, request.url.path)
    return JSONResponse(
        status_code=500,
        content={
            "code": 500,
            "message": "internal server error",
            "data": None,
        },
    )


@app.get("/health")
def health():
    return {"status": "ok"}


@app.get("/healthz")
def healthz():
    return {"status": "ok"}


@app.get("/readyz")
def readyz():
    database_ok = True
    database_error = None
    try:
        with engine.connect() as connection:
            connection.execute(text("SELECT 1"))
    except Exception as exc:  # noqa: BLE001 - report instead of crashing
        database_ok = False
        database_error = str(exc)[:200]

    status = disagg_service.status()
    models_ready = bool(status["appliances"])
    body = {
        "status": "ok" if database_ok and models_ready else "degraded",
        "database": {"ok": database_ok, "error": database_error},
        "inference": status,
        "models_ready": models_ready,
    }
    return JSONResponse(status_code=200 if body["status"] == "ok" else 503, content=body)
