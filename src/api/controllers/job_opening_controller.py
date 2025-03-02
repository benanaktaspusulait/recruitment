from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas, entities
from src.services.job_opening_service import JobOpeningService
from typing import List, Optional

class JobOpeningController:
    @staticmethod
    def get_job_openings(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        company_id: Optional[int] = None,
        status: Optional[entities.JobStatus] = None
    ) -> List[schemas.JobOpening]:
        return JobOpeningService.get_job_openings(db, skip, limit, company_id, status)

    @staticmethod
    def get_job_opening(db: Session, job_id: int) -> schemas.JobOpening:
        job = JobOpeningService.get_job_opening(db, job_id)
        if job is None:
            raise HTTPException(status_code=404, detail="Job opening not found")
        return job

    @staticmethod
    def create_job_opening(db: Session, job: schemas.JobOpeningCreate) -> schemas.JobOpening:
        try:
            return JobOpeningService.create_job_opening(db, job)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 