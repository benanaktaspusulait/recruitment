from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models import schemas
from src.api.controllers.candidate_controller import CandidateController

router = APIRouter(
    prefix="/candidates",
    tags=["Candidates"],
    responses={404: {"description": "Not found"}}
)

@router.get(
    "/",
    response_model=List[schemas.Candidate],
    summary="List all candidates",
    description="Get a list of all candidates with pagination support"
)
def get_candidates(
    skip: int = Query(0, ge=0, description="Number of candidates to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of candidates to return"),
    db: Session = Depends(get_db)
):
    return CandidateController.get_candidates(db, skip, limit)

@router.get(
    "/{candidate_id}",
    response_model=schemas.Candidate,
    summary="Get a specific candidate",
    responses={
        200: {
            "description": "Candidate details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "john.doe@example.com",
                        "phone": "+1234567890",
                        "skills": "Python, FastAPI, SQL",
                        "experience_years": 5
                    }
                }
            }
        }
    }
)
def get_candidate(
    candidate_id: int = Path(..., ge=1, description="The ID of the candidate to retrieve"),
    db: Session = Depends(get_db)
):
    return CandidateController.get_candidate(db, candidate_id)

@router.post(
    "/",
    response_model=schemas.Candidate,
    status_code=201,
    summary="Create a new candidate",
    responses={
        201: {"description": "Candidate created successfully"},
        400: {"description": "Candidate with this email already exists"}
    }
)
def create_candidate(
    candidate: schemas.CandidateCreate = Body(
        ...,
        example={
            "first_name": "John",
            "last_name": "Doe",
            "email": "john.doe@example.com",
            "phone": "+1234567890",
            "skills": "Python, FastAPI, SQL",
            "experience_years": 5,
            "current_company": "Tech Corp",
            "current_position": "Senior Developer",
            "education": "Bachelor's in Computer Science"
        }
    ),
    db: Session = Depends(get_db)
):
    return CandidateController.create_candidate(db, candidate)

@router.put(
    "/{candidate_id}",
    response_model=schemas.Candidate,
    summary="Update a candidate",
    responses={
        200: {"description": "Candidate updated successfully"},
        404: {"description": "Candidate not found"}
    }
)
def update_candidate(
    candidate_id: int = Path(..., ge=1),
    candidate: schemas.CandidateBase = Body(...),
    db: Session = Depends(get_db)
):
    return CandidateController.update_candidate(db, candidate_id, candidate) 