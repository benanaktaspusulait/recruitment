from sqlalchemy.orm import Session
from src.models import entities, schemas
from src.services.base_service import BaseService
from src.services.email_service import EmailService
from typing import List, Optional
from datetime import datetime, UTC
from fastapi import HTTPException

class InterviewProcessService(BaseService[entities.InterviewProcess]):
    def __init__(self):
        super().__init__(entities.InterviewProcess)
        self.logger = self.logger.bind(service="InterviewProcessService")
        self.email_service = EmailService()

    def start_interview_process(
        self,
        db: Session,
        application_id: int,
        current_user: entities.User
    ) -> entities.InterviewProcess:
        # Get application and verify it exists
        application = db.query(entities.Application).get(application_id)
        if not application:
            raise HTTPException(status_code=404, detail="Application not found")

        # Get job opening's interview template
        if not application.job_opening.interview_template_id:
            raise HTTPException(
                status_code=400,
                detail="Job opening has no interview template assigned"
            )

        # Create interview process
        process_data = {
            "application_id": application_id,
            "template_id": application.job_opening.interview_template_id,
            "current_step": 0,
            "status": entities.InterviewStepStatus.PENDING
        }
        
        process = self.create(db, process_data, current_user)

        # Create interview steps from template
        template = application.job_opening.interview_template
        for step in template.steps:
            step_data = {
                "process_id": process.id,
                "template_step_id": step.id,
                "order": step.order,
                "status": entities.InterviewStepStatus.PENDING
            }
            db_step = entities.InterviewStep(**step_data)
            db.add(db_step)

        db.commit()
        db.refresh(process)

        # Update application status
        application.status = entities.ApplicationStatus.INTERVIEWING
        db.commit()

        # Send email notification to candidate
        self._send_process_started_email(application)

        return process

    async def update_interview_step(
        self,
        db: Session,
        step_id: int,
        update: schemas.InterviewStepUpdate,
        current_user: entities.User
    ) -> entities.InterviewStep:
        step = db.query(entities.InterviewStep).get(step_id)
        if not step:
            raise HTTPException(status_code=404, detail="Interview step not found")

        # Update step
        update_data = update.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(step, key, value)

        # If status is being updated to completed, set completed_at
        if update.status == entities.InterviewStepStatus.COMPLETED:
            step.completed_at = datetime.now(UTC)

        db.commit()
        db.refresh(step)

        # Send email notifications
        if update.status == entities.InterviewStepStatus.SCHEDULED:
            await self._send_interview_scheduled_email(step)
        elif update.status in [entities.InterviewStepStatus.PASSED, entities.InterviewStepStatus.FAILED]:
            await self._send_interview_result_email(step)

        return step

    async def _send_process_started_email(self, application: entities.Application):
        data = {
            "candidate_name": f"{application.candidate.first_name} {application.candidate.last_name}",
            "job_title": application.job_opening.title,
            "company_name": application.job_opening.company.name
        }
        await self.email_service.send_email(
            db=None,
            to_email=application.candidate.email,
            template_type="interview_process_started",
            template_data=data,
            template_name=None
        )

    async def _send_interview_scheduled_email(self, step: entities.InterviewStep):
        data = {
            "candidate_name": f"{step.process.application.candidate.first_name}",
            "interview_type": step.template_step.name,
            "scheduled_at": step.scheduled_at,
            "duration": step.template_step.duration_minutes,
            "location": step.location or "Remote",
            "meeting_link": step.meeting_link
        }
        await self.email_service.send_email(
            db=None,
            to_email=step.process.application.candidate.email,
            template_type="interview_scheduled",
            template_data=data,
            template_name=None
        )

    async def _send_interview_result_email(self, step: entities.InterviewStep):
        is_success = step.status == entities.InterviewStepStatus.PASSED
        
        # Determine template type based on result
        template_type = "interview_success" if is_success else "interview_failure"
        
        # Check if this is the final interview step
        is_final_step = step.template_step.order == len(step.process.template.steps)

        data = {
            "candidate_name": f"{step.process.application.candidate.first_name}",
            "interview_type": step.template_step.name,
            "job_title": step.process.application.job_opening.title,
            "company_name": step.process.application.job_opening.company.name,
            "feedback": step.feedback or "No specific feedback provided.",
            "is_final_step": is_final_step
        }

        await self.email_service.send_email(
            db=None,
            to_email=step.process.application.candidate.email,
            template_type=template_type,
            template_data=data,
            template_name=None
        ) 