from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware as CORSMiddlewareClass
from src.database import engine, Base, SessionLocal
from src.database.seed import seed_database
from src.api.routes import companies, job_openings, candidates, applications, interviews, email_templates
from datetime import datetime, UTC
from src.core.logging import setup_logging
from src.core.config import get_settings
from src.core.middleware.db_profiler import DBProfilerMiddleware
from src.core.monitoring import setup_azure_monitoring
from sqlalchemy.exc import SQLAlchemyError
import typer

cli = typer.Typer()

@cli.command()
def run(
    seed: bool = typer.Option(
        False,
        "--seed",
        "-s",
        help="Seed the database with sample data"
    )
):
    """Run the FastAPI application"""
    if seed:
        logger.info("Seeding database...")
        db = SessionLocal()
        try:
            seed_database(db)
            logger.info("Database seeded successfully")
        finally:
            db.close()

    import uvicorn
    uvicorn.run("src.main:app", host="127.0.0.1", port=8000, reload=True)

# Setup logging
logger = setup_logging()
settings = get_settings()

logger.info("Starting application...")
# Create database tables
Base.metadata.create_all(bind=engine)

# Setup Azure monitoring in production
if settings.ENVIRONMENT == "production":
    setup_azure_monitoring(app, engine)

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

# Add database profiler middleware in non-production environments
if settings.ENVIRONMENT != "production":
    app.add_middleware(DBProfilerMiddleware)

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
    # Check database connection
    try:
        db = SessionLocal()
        try:
            # Test query
            db.execute("SELECT 1::integer")
            db_status = "healthy"
        except SQLAlchemyError as e:
            logger.error(f"Database health check failed: {str(e)}")
            db_status = "unhealthy"
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Database connection failed: {str(e)}")
        db_status = "unhealthy"

    return {
        "status": "healthy",
        "database": db_status,
        "timestamp": datetime.now(UTC).isoformat()
    }

if __name__ == "__main__":
    cli() 