from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional

class CompanyService(BaseService[entities.Company]):
    def __init__(self):
        super().__init__(entities.Company)

    def create_company(self, db: Session, company: schemas.CompanyCreate, current_user: entities.User) -> entities.Company:
        company_data = company.model_dump()
        return self.create(db, company_data, current_user)

    def update_company(
        self, 
        db: Session, 
        company_id: int, 
        company: schemas.CompanyBase,
        current_user: entities.User
    ) -> Optional[entities.Company]:
        company_data = company.model_dump()
        return self.update(db, company_id, company_data, current_user)

    def get_companies(self, db: Session, skip: int = 0, limit: int = 100) -> List[entities.Company]:
        return self.get_all(db, skip=skip, limit=limit)

    def get_company(self, db: Session, company_id: int) -> Optional[entities.Company]:
        return self.get_by_id(db, company_id)

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