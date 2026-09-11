import time
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import redis

from app.core.config import settings
from app.core.logging_config import log_activity
from app.database.database import engine, Base
from app.api.routes import api_router

# Auto-create tables for instant development/testing
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url="/api/openapi.json",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS setup
origins = settings.get_cors_origins()
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins if origins else ["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware for request logging & timing
@app.middleware("http")
async def add_process_time_and_log(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    return response

# Global Exception Handler
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    log_activity(f"Unhandled Exception on {request.url}: {str(exc)}", level="error")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error. Please try again later."}
    )

# Include Routers
app.include_router(api_router)

# Health Check Endpoint
@app.get("/health", tags=["Health"])
def health_check():
    db_status = "healthy"
    redis_status = "healthy"

    # Check DB
    try:
        with engine.connect() as conn:
            conn.execute(Base.metadata.tables.values().__iter__().__next__().select().limit(1))
    except Exception:
        db_status = "unhealthy"

    # Check Redis
    try:
        r = redis.Redis.from_url(settings.REDIS_URL, socket_timeout=2)
        r.ping()
    except Exception:
        redis_status = "unavailable (fallback to in-memory threads)"

    return {
        "status": "online" if db_status == "healthy" else "degraded",
        "version": settings.VERSION,
        "database": db_status,
        "redis_worker_queue": redis_status
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)

