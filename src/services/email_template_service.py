from sqlalchemy.orm import Session
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional
from jinja2 import Template
from fastapi import HTTPException

class EmailTemplateService(BaseService[entities.EmailTemplate]):
    def __init__(self):
        super().__init__(entities.EmailTemplate)
        self.logger = self.logger.bind(service="EmailTemplateService")

    def create_template(
        self,
        db: Session,
        template: schemas.EmailTemplateCreate,
        current_user: entities.User
    ) -> entities.EmailTemplate:
        # Validate template syntax
        try:
            Template(template.subject_template)
            Template(template.html_content)
        except Exception as e:
            raise ValueError(f"Invalid template syntax: {str(e)}")

        return self.create(db, template.model_dump(), current_user)

    def get_active_template(
        self,
        db: Session,
        template_type: str,
        name: Optional[str] = None
    ) -> entities.EmailTemplate:
        query = db.query(self.model).filter(
            self.model.type == template_type,
            self.model.is_active == True
        )
        
        if name:
            query = query.filter(self.model.name == name)
        
        template = query.first()
        if not template:
            raise HTTPException(
                status_code=404,
                detail=f"No active template found for type: {template_type}"
            )
        return template

    def render_template(
        self,
        template: entities.EmailTemplate,
        context: dict
    ) -> tuple[str, str]:
        try:
            # Render subject
            subject_template = Template(template.subject_template)
            subject = subject_template.render(**context)

            # Render content
            content_template = Template(template.html_content)
            content = content_template.render(**context)

            return subject, content
        except Exception as e:
            self.logger.error(f"Template rendering failed: {str(e)}")
            raise ValueError(f"Failed to render template: {str(e)}") 