from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum, func
from sqlalchemy.orm import relationship
from src.models.base_entity import BaseEntity
from datetime import datetime, UTC
import enum
import bcrypt

class JobStatus(enum.Enum):
    OPEN = "open"
    CLOSED = "closed"
    ON_HOLD = "on_hold"

class ApplicationStatus(enum.Enum):
    APPLIED = "applied"
    SCREENING = "screening"
    INTERVIEWING = "interviewing"
    OFFERED = "offered"
    HIRED = "hired"
    REJECTED = "rejected"
    WITHDRAWN = "withdrawn"

class UserRole(str, enum.Enum):
    CANDIDATE = "candidate"
    RECRUITER = "recruiter"
    ADMIN = "admin"

class InterviewStepStatus(str, enum.Enum):
    PENDING = "pending"
    SCHEDULED = "scheduled"
    COMPLETED = "completed"
    CANCELLED = "cancelled"
    FAILED = "failed"
    PASSED = "passed"

class InterviewStepType(str, enum.Enum):
    SCREENING = "screening"
    TECHNICAL = "technical"
    BEHAVIORAL = "behavioral"
    SYSTEM_DESIGN = "system_design"
    CODING = "coding"
    CULTURE_FIT = "culture_fit"
    HR = "hr"
    FINAL = "final"

class Company(BaseEntity):
    __tablename__ = "companies"

    name = Column(String, index=True)
    industry = Column(String)
    location = Column(String)
    website = Column(String)
    description = Column(Text)
    active = Column(Boolean, default=True)

    job_openings = relationship(
        "JobOpening",
        back_populates="company",
        cascade="all, delete-orphan"
    )

class JobOpening(BaseEntity):
    __tablename__ = "job_openings"

    title = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    interview_template_id = Column(Integer, ForeignKey("interview_templates.id"))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String)
    salary_range = Column(String)
    job_type = Column(String)  # full-time, part-time, contract
    experience_level = Column(String)
    status = Column(Enum(JobStatus), default=JobStatus.OPEN)

    company = relationship("Company", back_populates="job_openings")
    interview_template = relationship("InterviewTemplate", back_populates="job_openings")
    applications = relationship(
        "Application",
        back_populates="job_opening",
        cascade="all, delete-orphan"
    )

class Candidate(BaseEntity):
    __tablename__ = "candidates"

    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    first_name = Column(String, index=True)
    last_name = Column(String, index=True)
    email = Column(String, unique=True, index=True)
    phone = Column(String)
    resume_url = Column(String)
    linkedin_url = Column(String)
    skills = Column(Text)  # Comma-separated or JSON string
    experience_years = Column(Integer)
    current_company = Column(String)
    current_position = Column(String)
    education = Column(Text)  # JSON string containing education history
    available_from = Column(DateTime, nullable=True)
    notes = Column(Text)

    user = relationship("User", back_populates="candidate")
    applications = relationship(
        "Application",
        back_populates="candidate",
        cascade="all, delete-orphan"
    )

class Application(BaseEntity):
    __tablename__ = "applications"

    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(DateTime, default=lambda: datetime.now(UTC))
    resume_version = Column(String)  # Version of resume used for this application
    cover_letter = Column(Text)
    notes = Column(Text)
    interview_feedback = Column(Text)
    salary_expectation = Column(String)

    candidate = relationship("Candidate", back_populates="applications")
    job_opening = relationship("JobOpening", back_populates="applications")
    interview_process = relationship(
        "InterviewProcess",
        back_populates="application",
        uselist=False,
        cascade="all, delete-orphan"
    )

class User(BaseEntity):
    __tablename__ = "users"

    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATE)
    is_active = Column(Boolean, default=True)

    # Relationship with candidate if role is CANDIDATE
    candidate = relationship("Candidate", back_populates="user", uselist=False)

    def verify_password(self, password: str) -> bool:
        return bcrypt.checkpw(
            password.encode('utf-8'),
            self.hashed_password.encode('utf-8')
        )

    @staticmethod
    def hash_password(password: str) -> str:
        return bcrypt.hashpw(
            password.encode('utf-8'),
            bcrypt.gensalt()
        ).decode('utf-8')

class InterviewTemplate(BaseEntity):
    __tablename__ = "interview_templates"

    name = Column(String, index=True)
    description = Column(Text)
    is_active = Column(Boolean, default=True)

    steps = relationship(
        "InterviewTemplateStep",
        back_populates="template",
        cascade="all, delete-orphan",
        order_by="InterviewTemplateStep.order"
    )
    job_openings = relationship("JobOpening", back_populates="interview_template")

class InterviewTemplateStep(BaseEntity):
    __tablename__ = "interview_template_steps"

    template_id = Column(Integer, ForeignKey("interview_templates.id"))
    name = Column(String)
    description = Column(Text)
    step_type = Column(Enum(InterviewStepType))
    order = Column(Integer)
    duration_minutes = Column(Integer)
    required_participants = Column(Text)  # JSON array of roles/departments
    evaluation_criteria = Column(Text)    # JSON array of criteria
    passing_score = Column(Integer)       # Minimum score to pass

    template = relationship("InterviewTemplate", back_populates="steps")
    interview_steps = relationship("InterviewStep", back_populates="template_step")

class InterviewProcess(BaseEntity):
    __tablename__ = "interview_processes"

    application_id = Column(Integer, ForeignKey("applications.id"))
    template_id = Column(Integer, ForeignKey("interview_templates.id"))
    current_step = Column(Integer)
    status = Column(Enum(InterviewStepStatus), default=InterviewStepStatus.PENDING)
    notes = Column(Text)

    application = relationship("Application", back_populates="interview_process")
    template = relationship("InterviewTemplate")
    steps = relationship(
        "InterviewStep",
        back_populates="process",
        cascade="all, delete-orphan",
        order_by="InterviewStep.order"
    )

class InterviewStep(BaseEntity):
    __tablename__ = "interview_steps"

    process_id = Column(Integer, ForeignKey("interview_processes.id"))
    template_step_id = Column(Integer, ForeignKey("interview_template_steps.id"))
    order = Column(Integer)
    scheduled_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    status = Column(Enum(InterviewStepStatus), default=InterviewStepStatus.PENDING)
    score = Column(Integer, nullable=True)
    feedback = Column(Text)
    interviewer_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    meeting_link = Column(String, nullable=True)
    location = Column(String, nullable=True)

    process = relationship("InterviewProcess", back_populates="steps")
    template_step = relationship("InterviewTemplateStep", back_populates="interview_steps")
    interviewer = relationship("User", foreign_keys=[interviewer_id])

class EmailTemplate(BaseEntity):
    __tablename__ = "email_templates"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, nullable=False)
    description = Column(String)
    subject_template = Column(String, nullable=False)
    html_content = Column(Text, nullable=False)
    type = Column(String, nullable=False)  # e.g., 'interview_success', 'interview_failure'
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    created_by_id = Column(Integer, ForeignKey("users.id"))
    
    created_by = relationship("User", back_populates="email_templates") 