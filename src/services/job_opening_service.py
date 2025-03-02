from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from typing import List, Optional

class JobOpeningService:
    @staticmethod
    def get_job_openings(
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        company_id: Optional[int] = None,
        status: Optional[entities.JobStatus] = None
    ) -> List[entities.JobOpening]:
        query = db.query(entities.JobOpening)
        if company_id:
            query = query.filter(entities.JobOpening.company_id == company_id)
        if status:
            query = query.filter(entities.JobOpening.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_job_opening(db: Session, job_id: int) -> Optional[entities.JobOpening]:
        return db.query(entities.JobOpening).filter(entities.JobOpening.id == job_id).first()

    @staticmethod
    def create_job_opening(db: Session, job: schemas.JobOpeningCreate) -> entities.JobOpening:
        # Verify company exists
        company = db.query(entities.Company).filter(entities.Company.id == job.company_id).first()
        if not company:
            raise ValueError("Company not found")

        db_job = entities.JobOpening(**job.model_dump())
        try:
            db.add(db_job)
            db.commit()
            db.refresh(db_job)
            return db_job
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create job opening") 