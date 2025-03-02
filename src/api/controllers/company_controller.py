from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas
from src.services.company_service import CompanyService
from typing import List

class CompanyController:
    @staticmethod
    def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Company]:
        return CompanyService.get_companies(db, skip, limit)

    @staticmethod
    def get_company(db: Session, company_id: int) -> schemas.Company:
        company = CompanyService.get_company(db, company_id)
        if company is None:
            raise HTTPException(status_code=404, detail="Company not found")
        return company

    @staticmethod
    def create_company(db: Session, company: schemas.CompanyCreate) -> schemas.Company:
        try:
            return CompanyService.create_company(db, company)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def update_company(db: Session, company_id: int, company: schemas.CompanyBase) -> schemas.Company:
        try:
            updated_company = CompanyService.update_company(db, company_id, company)
            if updated_company is None:
                raise HTTPException(status_code=404, detail="Company not found")
            return updated_company
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 