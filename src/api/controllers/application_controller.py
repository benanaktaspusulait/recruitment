from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas, entities
from src.services.application_service import ApplicationService
from typing import List, Optional

class ApplicationController:
    @staticmethod
    def get_applications(
        db: Session,
        skip: int = 0,
        limit: int = 100,
        candidate_id: Optional[int] = None,
        job_opening_id: Optional[int] = None,
        status: Optional[entities.ApplicationStatus] = None
    ) -> List[schemas.Application]:
        return ApplicationService.get_applications(
            db, skip, limit, candidate_id, job_opening_id, status
        )

    @staticmethod
    def get_application(db: Session, application_id: int) -> schemas.Application:
        application = ApplicationService.get_application(db, application_id)
        if application is None:
            raise HTTPException(status_code=404, detail="Application not found")
        return application

    @staticmethod
    def create_application(db: Session, application: schemas.ApplicationCreate) -> schemas.Application:
        try:
            return ApplicationService.create_application(db, application)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def update_application_status(
        db: Session,
        application_id: int,
        update: schemas.ApplicationUpdate
    ) -> schemas.Application:
        try:
            updated_application = ApplicationService.update_application_status(
                db, application_id, update
            )
            if updated_application is None:
                raise HTTPException(status_code=404, detail="Application not found")
            return updated_application
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 