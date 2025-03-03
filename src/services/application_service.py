from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional
from datetime import datetime, UTC

class ApplicationService(BaseService[entities.Application]):
    def __init__(self):
        super().__init__(entities.Application)

    def get_applications(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100,
        candidate_id: Optional[int] = None,
        job_opening_id: Optional[int] = None,
        status: Optional[entities.ApplicationStatus] = None
    ) -> List[entities.Application]:
        filters = {}
        if candidate_id:
            filters['candidate_id'] = candidate_id
        if job_opening_id:
            filters['job_opening_id'] = job_opening_id
        if status:
            filters['status'] = status
        return self.get_all(db, skip=skip, limit=limit, **filters)

    def get_application(self, db: Session, application_id: int) -> Optional[entities.Application]:
        return self.get_by_id(db, application_id)

    def create_application(
        self,
        db: Session,
        application: schemas.ApplicationCreate,
        current_user: entities.User
    ) -> entities.Application:
        # Verify job opening exists and is open
        job = db.query(entities.JobOpening).filter(
            entities.JobOpening.id == application.job_opening_id
        ).first()
        if not job:
            raise ValueError("Job opening not found")
        if job.status != entities.JobStatus.OPEN:
            raise ValueError("Job opening is not accepting applications")

        # Check if candidate already applied
        existing = db.query(entities.Application).filter(
            entities.Application.candidate_id == application.candidate_id,
            entities.Application.job_opening_id == application.job_opening_id
        ).first()
        if existing:
            raise ValueError("Candidate has already applied for this position")

        application_data = application.model_dump()
        return self.create(db, application_data, current_user)

    def update_application_status(
        self,
        db: Session,
        application_id: int,
        update: schemas.ApplicationUpdate,
        current_user: entities.User
    ) -> Optional[entities.Application]:
        update_data = update.model_dump()
        return self.update(db, application_id, update_data, current_user) 