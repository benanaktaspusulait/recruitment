from fastapi import APIRouter, Depends, Query, Path, Body, HTTPException
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models import schemas, entities
from src.api.controllers.company_controller import CompanyController
from src.services.auth_service import AuthService
from src.services.company_service import CompanyService

router = APIRouter(
    prefix="/companies",
    tags=["Companies"],
    responses={404: {"description": "Not found"}}
)

company_controller = CompanyController()
company_service = CompanyService()

@router.get(
    "/",
    response_model=List[schemas.Company],
    summary="List all companies",
    description="Get a list of all companies with pagination support"
)
def get_companies(
    skip: int = Query(0, ge=0, description="Number of companies to skip"),
    limit: int = Query(100, ge=1, le=100, description="Maximum number of companies to return"),
    db: Session = Depends(get_db)
):
    return company_controller.get_companies(db, skip, limit)

@router.get(
    "/{company_id}",
    response_model=schemas.Company,
    summary="Get a specific company",
    responses={
        200: {
            "description": "Company details",
            "content": {
                "application/json": {
                    "example": {
                        "id": 1,
                        "name": "Tech Corp",
                        "industry": "Technology",
                        "location": "San Francisco, CA",
                        "website": "https://techcorp.com",
                        "description": "Leading technology company"
                    }
                }
            }
        }
    }
)
def get_company(
    company_id: int = Path(..., ge=1, description="The ID of the company to retrieve"),
    db: Session = Depends(get_db)
):
    return company_controller.get_company(db, company_id)

@router.post(
    "/",
    response_model=schemas.Company,
    status_code=201,
    summary="Create a new company",
    responses={
        201: {"description": "Company created successfully"},
        403: {"description": "Not authorized to create companies"},
        400: {"description": "Invalid request"}
    }
)
def create_company(
    company: schemas.CompanyCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: schemas.User = Depends(AuthService.get_current_active_user)
):
    if current_user.role != entities.UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create companies"
        )
    return company_service.create(db, company.dict())

@router.put(
    "/{company_id}",
    response_model=schemas.Company,
    summary="Update a company",
    responses={
        200: {"description": "Company updated successfully"},
        403: {"description": "Not authorized to update companies"},
        404: {"description": "Company not found"}
    }
)
def update_company(
    company_id: int = Path(..., ge=1),
    company: schemas.CompanyBase = Body(...),
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    return company_controller.update_company(db, company_id, company, current_user) 