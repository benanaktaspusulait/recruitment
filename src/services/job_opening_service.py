from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional

class JobOpeningService(BaseService[entities.JobOpening]):
    def __init__(self):
        super().__init__(entities.JobOpening)

    def get_job_openings(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[int] = None,
        status: Optional[entities.JobStatus] = None
    ) -> List[entities.JobOpening]:
        filters = {}
        if company_id:
            filters['company_id'] = company_id
        if status:
            filters['status'] = status
        return self.get_all(db, skip=skip, limit=limit, **filters)

    def get_job_opening(self, db: Session, job_id: int) -> Optional[entities.JobOpening]:
        return self.get_by_id(db, job_id)

    def create_job_opening(
        self,
        db: Session,
        job: schemas.JobOpeningCreate,
        current_user: entities.User
    ) -> entities.JobOpening:
        # Verify company exists
        company = db.query(entities.Company).filter(
            entities.Company.id == job.company_id
        ).first()
        if not company:
            raise ValueError("Company not found")

        job_data = job.model_dump()
        return self.create(db, job_data, current_user) 