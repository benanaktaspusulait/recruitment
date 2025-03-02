from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from src.database import Base
from datetime import datetime, UTC
import enum

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

class Company(Base):
    __tablename__ = "companies"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, index=True)
    industry = Column(String)
    location = Column(String)
    website = Column(String)
    description = Column(Text)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    active = Column(Boolean, default=True)

    job_openings = relationship("JobOpening", back_populates="company")

class JobOpening(Base):
    __tablename__ = "job_openings"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String)
    salary_range = Column(String)
    job_type = Column(String)  # full-time, part-time, contract
    experience_level = Column(String)
    status = Column(Enum(JobStatus), default=JobStatus.OPEN)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    company = relationship("Company", back_populates="job_openings")
    applications = relationship("Application", back_populates="job_opening")

class Candidate(Base):
    __tablename__ = "candidates"

    id = Column(Integer, primary_key=True, index=True)
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
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    available_from = Column(DateTime, nullable=True)
    notes = Column(Text)

    applications = relationship("Application", back_populates="candidate")

class Application(Base):
    __tablename__ = "applications"

    id = Column(Integer, primary_key=True, index=True)
    candidate_id = Column(Integer, ForeignKey("candidates.id"))
    job_opening_id = Column(Integer, ForeignKey("job_openings.id"))
    status = Column(Enum(ApplicationStatus), default=ApplicationStatus.APPLIED)
    applied_date = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    resume_version = Column(String)  # Version of resume used for this application
    cover_letter = Column(Text)
    notes = Column(Text)
    interview_feedback = Column(Text)
    salary_expectation = Column(String)

    candidate = relationship("Candidate", back_populates="applications")
    job_opening = relationship("JobOpening", back_populates="applications") 