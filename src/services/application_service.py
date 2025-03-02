from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from typing import List, Optional
from datetime import datetime, UTC

class ApplicationService:
    @staticmethod
    def get_applications(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        candidate_id: Optional[int] = None,
        job_opening_id: Optional[int] = None,
        status: Optional[entities.ApplicationStatus] = None
    ) -> List[entities.Application]:
        query = db.query(entities.Application)
        if candidate_id:
            query = query.filter(entities.Application.candidate_id == candidate_id)
        if job_opening_id:
            query = query.filter(entities.Application.job_opening_id == job_opening_id)
        if status:
            query = query.filter(entities.Application.status == status)
        return query.offset(skip).limit(limit).all()

    @staticmethod
    def get_application(db: Session, application_id: int) -> Optional[entities.Application]:
        return db.query(entities.Application).filter(
            entities.Application.id == application_id
        ).first()

    @staticmethod
    def create_application(db: Session, application: schemas.ApplicationCreate) -> entities.Application:
        # Verify candidate exists
        candidate = db.query(entities.Candidate).filter(
            entities.Candidate.id == application.candidate_id
        ).first()
        if not candidate:
            raise ValueError("Candidate not found")

        # Verify job opening exists and is open
        job = db.query(entities.JobOpening).filter(
            entities.JobOpening.id == application.job_opening_id
        ).first()
        if not job:
            raise ValueError("Job opening not found")
        if job.status != entities.JobStatus.OPEN:
            raise ValueError("Job opening is not accepting applications")

        # Check if candidate already applied
        existing_application = db.query(entities.Application).filter(
            entities.Application.candidate_id == application.candidate_id,
            entities.Application.job_opening_id == application.job_opening_id
        ).first()
        if existing_application:
            raise ValueError("Candidate has already applied for this position")

        db_application = entities.Application(**application.model_dump())
        try:
            db.add(db_application)
            db.commit()
            db.refresh(db_application)
            return db_application
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create application")

    @staticmethod
    def update_application_status(
        db: Session,
        application_id: int,
        update: schemas.ApplicationUpdate
    ) -> Optional[entities.Application]:
        db_application = db.query(entities.Application).filter(
            entities.Application.id == application_id
        ).first()
        if not db_application:
            return None

        db_application.status = update.status
        if update.interview_feedback:
            db_application.interview_feedback = update.interview_feedback
        if update.notes:
            db_application.notes = update.notes
        db_application.updated_at = datetime.now(UTC)

        try:
            db.commit()
            db.refresh(db_application)
            return db_application
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to update application") 