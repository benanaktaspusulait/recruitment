from fastapi import APIRouter, Depends, Query, Path, Body
from sqlalchemy.orm import Session
from typing import List
from src.database import get_db
from src.models import schemas, entities
from src.api.controllers.interview_template_controller import InterviewTemplateController
from src.api.controllers.interview_process_controller import InterviewProcessController
from src.services.auth_service import AuthService

router = APIRouter(
    prefix="/interviews",
    tags=["Interviews"],
    responses={404: {"description": "Not found"}}
)

template_controller = InterviewTemplateController()
process_controller = InterviewProcessController()

@router.get(
    "/templates",
    response_model=List[schemas.InterviewTemplate],
    summary="List interview templates",
    description="Get a list of all active interview templates"
)
def get_templates(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=100),
    db: Session = Depends(get_db)
):
    return template_controller.get_templates(db, skip, limit)

@router.post(
    "/templates",
    response_model=schemas.InterviewTemplate,
    status_code=201,
    summary="Create interview template",
    responses={
        201: {"description": "Template created successfully"},
        403: {"description": "Not authorized to create templates"}
    }
)
def create_template(
    template: schemas.InterviewTemplateCreate = Body(...),
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    return template_controller.create_template(db, template, current_user)

@router.post(
    "/applications/{application_id}/start",
    response_model=schemas.InterviewStep,
    status_code=201,
    summary="Start interview process",
    responses={
        201: {"description": "Interview process started successfully"},
        403: {"description": "Not authorized to start interview process"},
        404: {"description": "Application not found"}
    }
)
def start_interview_process(
    application_id: int = Path(..., ge=1),
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    return process_controller.start_process(db, application_id, current_user)

@router.put(
    "/steps/{step_id}",
    response_model=schemas.InterviewStep,
    summary="Update interview step",
    responses={
        200: {"description": "Step updated successfully"},
        403: {"description": "Not authorized to update step"},
        404: {"description": "Step not found"}
    }
)
def update_interview_step(
    step_id: int = Path(..., ge=1),
    update: schemas.InterviewStepUpdate = Body(...),
    db: Session = Depends(get_db),
    current_user: entities.User = Depends(AuthService.get_current_active_user)
):
    return process_controller.update_step(db, step_id, update, current_user) 