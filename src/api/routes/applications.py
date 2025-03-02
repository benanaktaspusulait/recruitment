from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.models import schemas, entities
from src.api.controllers.application_controller import ApplicationController

router = APIRouter(
    prefix="/applications",
    tags=["Applications"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/",
    response_model=List[schemas.Application],
    summary="List all applications",
    description="Get a list of all applications with optional filtering"
)
def get_applications(
    skip: int = Query(0, ge=0, description="Number of applications to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of applications to return"),
    candidate_id: Optional[int] = Query(None, description="Filter by candidate ID"),
    job_opening_id: Optional[int] = Query(None, description="Filter by job opening ID"),
    status: Optional[entities.ApplicationStatus] = Query(None, description="Filter by application status"),
    db: Session = Depends(get_db)
):
    return ApplicationController.get_applications(
        db, skip, limit, candidate_id, job_opening_id, status
    )

@router.get(
    "/{application_id}",
    response_model=schemas.Application,
    summary="Get a specific application",
    responses={
        200: {
            "description": "Application details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "candidate_id": 1,
                        "job_opening_id": 1,
                        "status": "applied",
                        "applied_date": "2024-03-19T10:00:00Z"
                    }
                }
            }
        }
    }
)
def get_application(
    application_id: int = Path(..., ge=1, description="The ID of the application to retrieve"),
    db: Session = Depends(get_db)
):
    return ApplicationController.get_application(db, application_id)

@router.post(
    "/",
    response_model=schemas.Application,
    status_code=201,
    summary="Create a new application",
    responses={
        201: {"description": "Application created successfully"},
        400: {
            "description": "Invalid request",
            "content": {
                "application/json": {
                    "examples": {
                        "duplicate": {
                            "value": {"detail": "Candidate has already applied for this position"}
                        },
                        "closed": {
                            "value": {"detail": "Job opening is not accepting applications"}
                        }
                    }
                }
            }
        }
    }
)
def create_application(
    application: schemas.ApplicationCreate = Body(
        ...,
        example={
            "candidate_id": 1,
            "job_opening_id": 1,
            "cover_letter": "I am excited to apply...",
            "salary_expectation": "$120,000 - $140,000"
        }
    ),
    db: Session = Depends(get_db)
):
    return ApplicationController.create_application(db, application)

@router.put(
    "/{application_id}/status",
    response_model=schemas.Application,
    summary="Update application status",
    description="Update the status of an application and optionally add feedback",
    responses={
        200: {"description": "Application status updated successfully"},
        404: {"description": "Application not found"}
    }
)
def update_application_status(
    application_id: int = Path(..., ge=1),
    update: schemas.ApplicationUpdate = Body(
        ...,
        example={
            "status": "interviewing",
            "interview_feedback": "Great technical skills, moving to next round",
            "notes": "Scheduled for technical interview"
        }
    ),
    db: Session = Depends(get_db)
):
    return ApplicationController.update_application_status(db, application_id, update) 