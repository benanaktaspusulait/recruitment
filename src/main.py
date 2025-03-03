from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORSMiddlewareClass
from src.database import engine, Base
from src.api.routes import companies, job_openings, candidates, applications, interviews, email_templates
from datetime import datetime, UTC
from src.core.logging import setup_logging
from src.core.config import get_settings

# Setup logging
logger = setup_logging()
settings = get_settings()

logger.info("Starting application...")
# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recruitment System API",
    description="REST API for managing job openings, candidates, and applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)
logger.info("FastAPI application configured")

# Add CORS middleware
app.add_middleware(
    CORSMiddlewareClass,
    allow_credentials=True,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(companies.router, prefix="/v1", tags=["Companies"])
app.include_router(job_openings.router, prefix="/v1", tags=["Job Openings"])
app.include_router(candidates.router, prefix="/v1", tags=["Candidates"])
app.include_router(applications.router, prefix="/v1", tags=["Applications"])
app.include_router(interviews.router, prefix="/v1", tags=["Interviews"])
app.include_router(email_templates.router, prefix="/v1", tags=["Email Templates"])

@app.get("/")
async def root():
    return {
        "name": "Recruitment System API",
        "version": "1.0.0",
        "documentation": "/docs",
        "alternative_documentation": "/redoc"
    }

@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now(UTC).isoformat()
    } 