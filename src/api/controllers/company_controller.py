from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas, entities
from src.services.company_service import CompanyService
from typing import List

class CompanyController:
    def __init__(self):
        self.service = CompanyService()

    def get_companies(self, db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Company]:
        return self.service.get_companies(db, skip, limit)

    def get_company(self, db: Session, company_id: int) -> schemas.Company:
        company = self.service.get_company(db, company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    def create_company(
        self, 
        db: Session, 
        company: schemas.CompanyCreate,
        current_user: entities.User
    ) -> schemas.Company:
        if current_user.role not in [entities.UserRole.RECRUITER, entities.UserRole.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only recruiters and admins can create companies"
            )
        try:
            return self.service.create_company(db, company, current_user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    def update_company(
        self,
        db: Session,
        company_id: int,
        company: schemas.CompanyBase,
        current_user: entities.User
    ) -> schemas.Company:
        if current_user.role not in [entities.UserRole.RECRUITER, entities.UserRole.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only recruiters and admins can update companies"
            )
        try:
            updated_company = self.service.update_company(db, company_id, company, current_user)
            if updated_company is None:
                raise HTTPException(status_code=404, detail="Company not found")
            return updated_company
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 