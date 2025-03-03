from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas, entities
from src.services.interview_template_service import InterviewTemplateService
from typing import List

class InterviewTemplateController:
    def __init__(self):
        self.service = InterviewTemplateService()

    def get_templates(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[schemas.InterviewTemplate]:
        return self.service.get_active_templates(db, skip, limit)

    def create_template(
        self,
        db: Session,
        template: schemas.InterviewTemplateCreate,
        current_user: entities.User
    ) -> schemas.InterviewTemplate:
        if current_user.role not in [entities.UserRole.RECRUITER, entities.UserRole.ADMIN]:
            raise HTTPException(
                status_code=403,
                detail="Only recruiters and admins can create interview templates"
            )
        try:
            return self.service.create_template(db, template, current_user)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 