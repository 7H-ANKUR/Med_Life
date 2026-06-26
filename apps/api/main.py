from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded
from contextlib import asynccontextmanager
import sentry_sdk

from config import settings
from database import engine, Base
from routers import auth, symptoms, places, fees, saved, history, feedback, users


# ─── Sentry (production only) ────────────────────────────
if settings.environment == "production" and settings.sentry_dsn:
    sentry_sdk.init(dsn=settings.sentry_dsn, environment=settings.environment)


# ─── Rate Limiter ─────────────────────────────────────────
limiter = Limiter(key_func=get_remote_address)


# ─── App Lifespan ─────────────────────────────────────────
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: create tables (handled by alembic in prod, auto-create in dev)
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Shutdown
    await engine.dispose()


# ─── FastAPI App ──────────────────────────────────────────
app = FastAPI(
    title="Travel Health Finder API",
    description="Location-aware medical recommendation API for travelers",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

# Rate limiter state
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

# CORS
origins = [o.strip() for o in settings.allowed_origins.split(",")]
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ─── Routers ──────────────────────────────────────────────
app.include_router(auth.router,      prefix="/v1/auth",    tags=["Auth"])
app.include_router(users.router,     prefix="/v1/users",   tags=["Users"])
app.include_router(symptoms.router,  prefix="/v1",         tags=["Symptoms"])
app.include_router(places.router,    prefix="/v1/places",  tags=["Places"])
app.include_router(fees.router,      prefix="/v1",         tags=["Fees"])
app.include_router(saved.router,     prefix="/v1/saved",   tags=["Saved"])
app.include_router(history.router,   prefix="/v1/history", tags=["History"])
app.include_router(feedback.router,  prefix="/v1",         tags=["Feedback"])


# ─── Health Check ─────────────────────────────────────────
@app.get("/health", tags=["Health"])
async def health():
    return {"status": "ok", "environment": settings.environment}
