from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from typing import List, Optional

class CompanyService:
    @staticmethod
    def get_companies(db: Session, skip: int = 0, limit: int = 100) -> List[entities.Company]:
        return db.query(entities.Company).offset(skip).limit(limit).all()

    @staticmethod
    def get_company(db: Session, company_id: int) -> Optional[entities.Company]:
        return db.query(entities.Company).filter(entities.Company.id == company_id).first()

    @staticmethod
    def create_company(db: Session, company: schemas.CompanyCreate) -> entities.Company:
        db_company = entities.Company(**company.model_dump())
        try:
            db.add(db_company)
            db.commit()
            db.refresh(db_company)
            return db_company
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create company")

    @staticmethod
    def update_company(db: Session, company_id: int, company: schemas.CompanyBase) -> Optional[entities.Company]:
        db_company = db.query(entities.Company).filter(entities.Company.id == company_id).first()
        if db_company:
            for key, value in company.model_dump().items():
                setattr(db_company, key, value)
            try:
                db.commit()
                db.refresh(db_company)
                return db_company
            except IntegrityError:
                db.rollback()
                raise ValueError("Failed to update company")
        return None 