from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas, entities
from src.services.interview_process_service import InterviewProcessService
from typing import List

class InterviewProcessController:
    def __init__(self):
        self.service = InterviewProcessService()

    def start_process(
        self,
        db: Session,
        application_id: int,
        current_user: entities.User
    ) -> schemas.InterviewStep:
        if current_user.role not in [entities.UserRole.RECRUITER, entities.UserRole.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only recruiters and admins can start interview processes"
            )
        try:
            return self.service.start_interview_process(db, application_id, current_user)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e))

    async def update_step(
        self,
        db: Session,
        step_id: int,
        update: schemas.InterviewStepUpdate,
        current_user: entities.User
    ) -> schemas.InterviewStep:
        if current_user.role not in [entities.UserRole.RECRUITER, entities.UserRole.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only recruiters and admins can update interview steps"
            )
        try:
            return await self.service.update_interview_step(db, step_id, update, current_user)
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=400, detail=str(e)) 