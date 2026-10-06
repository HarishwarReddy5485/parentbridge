# Compatibility fix for Python 3.9 + Pydantic v2.13 + typing-inspection
# Python 3.9 typing.Literal does not automatically flatten nested Literals, which breaks OpenAPI generation
import typing_inspection.introspection
import pydantic.json_schema
_orig_get_literal_values = typing_inspection.introspection.get_literal_values
def _compat_get_literal_values(annotation, **kwargs):
    for val in _orig_get_literal_values(annotation, **kwargs):
        if hasattr(val, "__args__") and not isinstance(val, str):
            yield from _compat_get_literal_values(val, **kwargs)
        else:
            yield val
typing_inspection.introspection.get_literal_values = _compat_get_literal_values
pydantic.json_schema.get_literal_values = _compat_get_literal_values

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager

from app.config import settings
from app.database import engine, Base
from app.routes.auth import router as auth_router
from app.routes.admin import router as admin_router
from app.routes.class_teacher import router as class_teacher_router
from app.routes.teacher import router as teacher_router
from app.routes.parent import router as parent_router
from app.routes.student import router as student_router
from app.routes.assignments import router as assignments_router
from app.routes.grades import router as grades_router
from app.routes.attendance import router as attendance_router
from app.routes.notices import router as notices_router
from app.routes.messages import router as messages_router
from app.websocket.router import router as websocket_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifespan context manager for database connection pool handling."""
    # Ensure tables exist on startup if running local/dev
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    yield
    # Dispose connection pool on shutdown
    await engine.dispose()


app = FastAPI(
    title=settings.APP_NAME,
    description="ParentBridge: Parent-Teacher Communication & Student Progress Portal API",
    version="1.0.0",
    lifespan=lifespan,
    docs_url="/docs",
    redoc_url="/redoc",
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register REST Routers
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(class_teacher_router)
app.include_router(teacher_router)
app.include_router(parent_router)
app.include_router(student_router)
app.include_router(assignments_router)
app.include_router(grades_router)
app.include_router(attendance_router)
app.include_router(notices_router)
app.include_router(messages_router)

# Register WebSocket Router
app.include_router(websocket_router)


@app.get("/", tags=["Health Check"])
async def root_health_check():
    """Service health and diagnostic status endpoint."""
    return {
        "status": "healthy",
        "app": settings.APP_NAME,
        "environment": settings.APP_ENV,
        "version": "1.0.0",
        "docs": "/docs"
    }
