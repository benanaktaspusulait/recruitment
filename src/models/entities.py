from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text, Enum
from sqlalchemy.orm import relationship
from src.database import Base
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

class Company(Base, BaseEntity):
    __tablename__ = "companies"

    name = Column(String, index=True)
    industry = Column(String)
    location = Column(String)
    website = Column(String)
    description = Column(Text)
    active = Column(Boolean, default=True)

    job_openings = relationship("JobOpening", back_populates="company")
    created_by = relationship("User", foreign_keys=[BaseEntity.created_by_id])
    updated_by = relationship("User", foreign_keys=[BaseEntity.updated_by_id])

class JobOpening(Base, BaseEntity):
    __tablename__ = "job_openings"

    title = Column(String, index=True)
    company_id = Column(Integer, ForeignKey("companies.id"))
    description = Column(Text)
    requirements = Column(Text)
    location = Column(String)
    salary_range = Column(String)
    job_type = Column(String)  # full-time, part-time, contract
    experience_level = Column(String)
    status = Column(Enum(JobStatus), default=JobStatus.OPEN)

    company = relationship("Company", back_populates="job_openings")
    applications = relationship("Application", back_populates="job_opening")
    created_by = relationship("User", foreign_keys=[BaseEntity.created_by_id])
    updated_by = relationship("User", foreign_keys=[BaseEntity.updated_by_id])

class Candidate(Base, BaseEntity):
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
    applications = relationship("Application", back_populates="candidate")
    created_by = relationship("User", foreign_keys=[BaseEntity.created_by_id])
    updated_by = relationship("User", foreign_keys=[BaseEntity.updated_by_id])

class Application(Base, BaseEntity):
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
    created_by = relationship("User", foreign_keys=[BaseEntity.created_by_id])
    updated_by = relationship("User", foreign_keys=[BaseEntity.updated_by_id])

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True)
    hashed_password = Column(String)
    role = Column(Enum(UserRole), default=UserRole.CANDIDATE)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

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