from fastapi import HTTPException
from jinja2 import Environment, FileSystemLoader, select_autoescape
import aiosmtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from pathlib import Path
from loguru import logger
from typing import Dict, Any, Optional
from src.core.config import get_settings
from src.services.email_template_service import EmailTemplateService
from sqlalchemy.orm import Session

class EmailService:
    def __init__(self):
        self.logger = logger.bind(service="EmailService")
        self.template_service = EmailTemplateService()
        
        # Email configuration
        settings = get_settings()
        self.smtp_host = settings.SMTP_HOST
        self.smtp_port = settings.SMTP_PORT
        self.smtp_user = settings.SMTP_USER
        self.smtp_password = settings.SMTP_PASSWORD
        self.from_email = settings.FROM_EMAIL

    async def send_email(
        self,
        db: Session,
        to_email: str,
        template_type: str,
        *,
        template_name: Optional[str] = None,
        template_data: Dict[str, Any]
    ) -> None:
        try:
            # Get and render template
            template = self.template_service.get_active_template(
                db, template_type, template_name
            )
            subject, html_content = self.template_service.render_template(
                template, template_data
            )

            # Create message
            message = MIMEMultipart()
            message["From"] = self.from_email
            message["To"] = to_email
            message["Subject"] = subject

            # Add HTML content
            html_part = MIMEText(html_content, "html")
            message.attach(html_part)

            # Send email
            await aiosmtplib.send(
                message,
                hostname=self.smtp_host,
                port=self.smtp_port,
                username=self.smtp_user,
                password=self.smtp_password,
                use_tls=True
            )

            self.logger.info(f"Email sent successfully to {to_email}")
        except Exception as e:
            self.logger.error(f"Failed to send email to {to_email}: {str(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Failed to send email: {str(e)}"
            ) 