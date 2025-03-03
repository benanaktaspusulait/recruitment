from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List, Optional
from src.database import get_db
from src.models import schemas, entities
from src.services.email_template_service import EmailTemplateService
from src.services.auth_service import AuthService

router = APIRouter(
    prefix="/email-templates",
    tags=["Email Templates"]
)

template_service = EmailTemplateService()

@router.post(
    "/",
    response_model=schemas.EmailTemplate,
    status_code=201
)
def create_template(
    template: schemas.EmailTemplateCreate,
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    if current_user.role != entities.UserRole.ADMIN:
        raise HTTPException(
            status_code=403,
            detail="Only admins can create email templates"
        )
    return template_service.create_template(db, template, current_user)

@router.get(
    "/",
    response_model=List[schemas.EmailTemplate]
)
def list_templates(
    type: Optional[str] = None,
    is_active: bool = True,
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    return template_service.get_all(
        db,
        type=type,
        is_active=is_active
    ) 