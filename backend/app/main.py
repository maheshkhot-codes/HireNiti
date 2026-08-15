from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy import text

from app.database.database import engine

from app.auth.routes import router as auth_router
from app.candidates.routes import router as candidate_router
from app.recruiters.routes import router as recruiter_router
from app.jobs.routes import router as jobs_router
from app.companies.routes import router as companies_router
from app.resume.routes import router as resume_router
from app.applications.routes import (
    router as applications_router
)
from app.recruiters.dashboard_routes import (
    router as recruiter_dashboard_router
)




app = FastAPI(
    title="AI Recruitment System",
    description="AI-powered recruitment platform",
    version="1.0.0"
)
app.add_middleware(
    CORSMiddleware,

    allow_origins=[
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "https://hire-niti.vercel.app"
],

    allow_credentials=True,

    allow_methods=["*"],

    allow_headers=["*"]
)


# Register API routers
app.include_router(auth_router)
app.include_router(candidate_router)
app.include_router(recruiter_router)
app.include_router(jobs_router)
app.include_router(companies_router)
app.include_router(resume_router)
app.include_router(
    applications_router
)
app.include_router(
    recruiter_dashboard_router
)


@app.get("/")
def root():
    return {
        "message": "AI Recruitment System API is running"
    }


@app.get("/health")
def health_check():

    try:

        with engine.connect() as connection:

            connection.execute(
                text("SELECT 1")
            )

        return {
            "status": "healthy",
            "database": "connected"
        }

    except Exception:

        return {
            "status": "unhealthy",
            "database": "disconnected"
        }