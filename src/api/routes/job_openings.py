from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.models import schemas, entities
from src.api.controllers.job_opening_controller import JobOpeningController

router = APIRouter(
    prefix="/job-openings",
    tags=["Job Openings"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/",
    response_model=List[schemas.JobOpening],
    summary="List all job openings",
    description="Get a list of all job openings with optional filtering"
)
def get_job_openings(
    skip: int = Query(0, ge=0, description="Number of jobs to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of jobs to return"),
    company_id: Optional[int] = Query(None, description="Filter by company ID"),
    status: Optional[entities.JobStatus] = Query(None, description="Filter by job status"),
    db: Session = Depends(get_db)
):
    return JobOpeningController.get_job_openings(db, skip, limit, company_id, status)

@router.get(
    "/{job_id}",
    response_model=schemas.JobOpening,
    summary="Get a specific job opening"
)
def get_job_opening(
    job_id: int = Path(..., ge=1, description="The ID of the job opening to retrieve"),
    db: Session = Depends(get_db)
):
    return JobOpeningController.get_job_opening(db, job_id)

@router.post(
    "/",
    response_model=schemas.JobOpening,
    status_code=201,
    summary="Create a new job opening",
    responses={
        201: {"description": "Job opening created successfully"},
        400: {"description": "Invalid request"},
        404: {"description": "Company not found"}
    }
)
def create_job_opening(
    job: schemas.JobOpeningCreate = Body(
        ...,
        example={
            "title": "Senior Software Engineer",
            "company_id": 1,
            "description": "We are looking for a senior software engineer...",
            "requirements": "5+ years of experience...",
            "location": "San Francisco, CA",
            "salary_range": "$120,000 - $180,000",
            "job_type": "full-time",
            "experience_level": "Senior"
        }
    ),
    db: Session = Depends(get_db)
):
    return JobOpeningController.create_job_opening(db, job) 