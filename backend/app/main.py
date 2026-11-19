import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from postgrest.exceptions import APIError

from app.core.config import settings
from app.core.exceptions import DomainError
from app.routers import tasks

logger = logging.getLogger("app")

app = FastAPI(title="Multi-Tenant Task API", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH"],
    allow_headers=["Authorization", "Content-Type"],
)

app.include_router(tasks.router)

_DB_ERROR_STATUS = {"23503": 422, "23514": 422, "22P02": 422, "42501": 403}


@app.exception_handler(DomainError)
async def domain_error_handler(request: Request, exc: DomainError):
    return JSONResponse(status_code=exc.status_code, content={"detail": exc.detail})


@app.exception_handler(APIError)
async def database_error_handler(request: Request, exc: APIError):
    logger.error("Database error on %s: %s", request.url.path, exc)
    status_code = _DB_ERROR_STATUS.get(str(exc.code), 502)
    detail = "Request rejected by database" if status_code != 502 else "Database error"
    return JSONResponse(status_code=status_code, content={"detail": detail})


@app.exception_handler(Exception)
async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception("Unhandled error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


@app.get("/health")
def health():
    return {"status": "ok"}