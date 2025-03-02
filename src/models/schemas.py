from pydantic import BaseModel, EmailStr, HttpUrl, constr
from pydantic.types import constr
from typing import Optional, List
from datetime import datetime
from src.models.entities import JobStatus, ApplicationStatus

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