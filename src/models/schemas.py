from pydantic import BaseModel, EmailStr, HttpUrl, constr, SecretStr
from pydantic.types import constr
from typing import Optional, List
from datetime import datetime
from src.models.entities import JobStatus, ApplicationStatus, UserRole, InterviewStepStatus, InterviewStepType

# Company Schemas
class CompanyBase(BaseModel):
    name: str
    industry: str
    location: str
    website: Optional[HttpUrl] = None
    description: Optional[str] = None

class CompanyCreate(CompanyBase):
    pass

class Company(CompanyBase):
    id: int
    created_at: datetime
    active: bool
    
    class Config:
        from_attributes = True

# Job Opening Schemas
class JobOpeningBase(BaseModel):
    title: str
    description: str
    requirements: str
    location: str
    salary_range: Optional[str] = None
    job_type: str = constr(pattern='^(full-time|part-time|contract)$')
    experience_level: str
    status: JobStatus = JobStatus.OPEN

class JobOpeningCreate(JobOpeningBase):
    company_id: int

class JobOpening(JobOpeningBase):
    id: int
    company_id: int
    created_at: datetime
    updated_at: datetime
    company: Company
    
    class Config:
        from_attributes = True

# Candidate Schemas
class CandidateBase(BaseModel):
    first_name: str
    last_name: str
    email: EmailStr
    phone: Optional[str] = None
    resume_url: Optional[HttpUrl] = None
    linkedin_url: Optional[HttpUrl] = None
    skills: str
    experience_years: int
    current_company: Optional[str] = None
    current_position: Optional[str] = None
    education: str
    available_from: Optional[datetime] = None
    notes: Optional[str] = None

class CandidateCreate(CandidateBase):
    pass

class Candidate(CandidateBase):
    id: int
    created_at: datetime
    updated_at: datetime
    
    class Config:
        from_attributes = True

# Application Schemas
class ApplicationBase(BaseModel):
    resume_version: Optional[str] = None
    cover_letter: Optional[str] = None
    notes: Optional[str] = None
    salary_expectation: Optional[str] = None

class ApplicationCreate(ApplicationBase):
    candidate_id: int
    job_opening_id: int

class ApplicationUpdate(BaseModel):
    status: ApplicationStatus
    interview_feedback: Optional[str] = None
    notes: Optional[str] = None

class Application(ApplicationBase):
    id: int
    candidate_id: int
    job_opening_id: int
    status: ApplicationStatus
    applied_date: datetime
    updated_at: datetime
    interview_feedback: Optional[str] = None
    candidate: Candidate
    job_opening: JobOpening
    
    class Config:
        from_attributes = True

# Auth Schemas
class UserBase(BaseModel):
    email: EmailStr

class UserCreate(UserBase):
    password: SecretStr
    role: UserRole = UserRole.CANDIDATE
    
    # If role is candidate, these are required
    first_name: Optional[str] = None
    last_name: Optional[str] = None
    phone: Optional[str] = None

class User(UserBase):
    id: int
    role: UserRole
    is_active: bool
    created_at: datetime
    
    class Config:
        from_attributes = True

class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"

class TokenData(BaseModel):
    email: str
    role: UserRole

class InterviewTemplateStepBase(BaseModel):
    name: str
    description: str
    step_type: InterviewStepType
    order: int
    duration_minutes: int
    required_participants: list[str]
    evaluation_criteria: list[str]
    passing_score: int

class InterviewTemplateBase(BaseModel):
    name: str
    description: str
    is_active: bool = True

class InterviewTemplateCreate(InterviewTemplateBase):
    steps: list[InterviewTemplateStepBase]

class InterviewTemplate(InterviewTemplateBase):
    id: int
    steps: list[InterviewTemplateStepBase]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class InterviewStepUpdate(BaseModel):
    scheduled_at: Optional[datetime] = None
    status: Optional[InterviewStepStatus] = None
    score: Optional[int] = None
    feedback: Optional[str] = None
    interviewer_id: Optional[int] = None
    meeting_link: Optional[str] = None
    location: Optional[str] = None

class InterviewStep(BaseModel):
    id: int
    order: int
    scheduled_at: Optional[datetime]
    completed_at: Optional[datetime]
    status: InterviewStepStatus
    score: Optional[int]
    feedback: Optional[str]
    interviewer_id: Optional[int]
    meeting_link: Optional[str]
    location: Optional[str]
    template_step: InterviewTemplateStepBase

    class Config:
        from_attributes = True

class EmailTemplateBase(BaseModel):
    name: str
    description: Optional[str] = None
    subject_template: str
    html_content: str
    type: str
    is_active: bool = True

class EmailTemplateCreate(EmailTemplateBase):
    pass

class EmailTemplate(EmailTemplateBase):
    id: int
    created_at: datetime
    updated_at: Optional[datetime] = None
    created_by_id: int

    class Config:
        from_attributes = True 