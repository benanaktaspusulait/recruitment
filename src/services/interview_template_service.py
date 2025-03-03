from sqlalchemy.orm import Session
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional
import json

class InterviewTemplateService(BaseService[entities.InterviewTemplate]):
    def __init__(self):
        super().__init__(entities.InterviewTemplate)
        self.logger = self.logger.bind(service="InterviewTemplateService")

    def create_template(
        self,
        db: Session,
        template: schemas.InterviewTemplateCreate,
        current_user: entities.User
    ) -> entities.InterviewTemplate:
        self.logger.info(f"Creating interview template: {template.name}")
        
        # Create template
        template_data = template.model_dump(exclude={'steps'})
        db_template = self.create(db, template_data, current_user)

        # Create steps
        for step in template.steps:
            step_data = step.model_dump()
            step_data['required_participants'] = json.dumps(step.required_participants)
            step_data['evaluation_criteria'] = json.dumps(step.evaluation_criteria)
            
            db_step = entities.InterviewTemplateStep(
                template_id=db_template.id,
                **step_data
            )
            db.add(db_step)
        
        db.commit()
        db.refresh(db_template)
        return db_template

    def get_active_templates(
        self,
        db: Session,
        skip: int = 0,
        limit: int = 100
    ) -> List[entities.InterviewTemplate]:
        return self.get_all(db, skip=skip, limit=limit, is_active=True) 