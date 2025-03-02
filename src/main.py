from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORSMiddlewareClass
from src.database import engine, Base
from src.api.routes import companies, job_openings
from datetime import datetime, UTC

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Recruitment System API",
    description="REST API for managing job openings, candidates, and applications",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

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