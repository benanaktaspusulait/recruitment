from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from src.models import entities, schemas
from src.services.base_service import BaseService
from typing import List, Optional

class CandidateService(BaseService[entities.Candidate]):
    def __init__(self):
        super().__init__(entities.Candidate)

    def get_candidates(self, db: Session, skip: int = 0, limit: int = 100) -> List[entities.Candidate]:
        return self.get_all(db, skip=skip, limit=limit)

    def get_candidate(self, db: Session, candidate_id: int) -> Optional[entities.Candidate]:
        return self.get_by_id(db, candidate_id)

    def create_candidate(
        self,
        db: Session,
        candidate: schemas.CandidateCreate,
        current_user: entities.User
    ) -> entities.Candidate:
        # Check if candidate with email already exists
        if db.query(entities.Candidate).filter(
            entities.Candidate.email == candidate.email
        ).first():
            raise ValueError(f"Candidate with email {candidate.email} already exists")

        candidate_data = candidate.model_dump()
        return self.create(db, candidate_data, current_user)

    def update_candidate(
        self,
        db: Session,
        candidate_id: int,
        candidate: schemas.CandidateBase,
        current_user: entities.User
    ) -> Optional[entities.Candidate]:
        candidate_data = candidate.model_dump()
        return self.update(db, candidate_id, candidate_data, current_user) 