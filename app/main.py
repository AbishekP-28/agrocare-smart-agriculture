from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.middleware.sessions import SessionMiddleware
from app.database import engine, Base
from app.routes import auth, pages, fields, readings, recommendations, analytics, simulate
from pathlib import Path

# Create tables
Base.metadata.create_all(bind=engine)

app = FastAPI(title="AgroCare - Smart Agriculture")

# Session middleware (for login)
app.add_middleware(SessionMiddleware, secret_key="agrocare-secret-key-2024")

# Serve static files
static_dir = Path(__file__).resolve().parent.parent / "static"
static_dir.mkdir(exist_ok=True)
app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

# Include routers
app.include_router(auth.router)
app.include_router(pages.router)
app.include_router(fields.router)
app.include_router(readings.router)
app.include_router(recommendations.router)
app.include_router(analytics.router)
app.include_router(simulate.router)

@app.get("/health")
def health_check():
    return {"status": "ok"}