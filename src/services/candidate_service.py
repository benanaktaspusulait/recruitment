from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from typing import List, Optional

class CandidateService:
    @staticmethod
    def get_candidates(db: Session, skip: int = 0, limit: int = 100) -> List[entities.Candidate]:
        return db.query(entities.Candidate).offset(skip).limit(limit).all()

    @staticmethod
    def get_candidate(db: Session, candidate_id: int) -> Optional[entities.Candidate]:
        return db.query(entities.Candidate).filter(entities.Candidate.id == candidate_id).first()

    @staticmethod
    def create_candidate(db: Session, candidate: schemas.CandidateCreate) -> entities.Candidate:
        # Check if candidate with email already exists
        existing_candidate = db.query(entities.Candidate).filter(
            entities.Candidate.email == candidate.email
        ).first()
        if existing_candidate:
            raise ValueError(f"Candidate with email {candidate.email} already exists")

        db_candidate = entities.Candidate(**candidate.model_dump())
        try:
            db.add(db_candidate)
            db.commit()
            db.refresh(db_candidate)
            return db_candidate
        except IntegrityError:
            db.rollback()
            raise ValueError("Failed to create candidate")

    @staticmethod
    def update_candidate(
        db: Session, 
        candidate_id: int, 
        candidate: schemas.CandidateBase
    ) -> Optional[entities.Candidate]:
        db_candidate = db.query(entities.Candidate).filter(
            entities.Candidate.id == candidate_id
        ).first()
        if db_candidate:
            for key, value in candidate.model_dump().items():
                setattr(db_candidate, key, value)
            try:
                db.commit()
                db.refresh(db_candidate)
                return db_candidate
            except IntegrityError:
                db.rollback()
                raise ValueError("Failed to update candidate")
        return None 