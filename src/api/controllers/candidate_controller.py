from fastapi import HTTPException
from sqlalchemy.orm import Session
from src.models import schemas
from src.services.candidate_service import CandidateService
from typing import List

class CandidateController:
    @staticmethod
    def get_candidates(db: Session, skip: int = 0, limit: int = 100) -> List[schemas.Candidate]:
        return CandidateService.get_candidates(db, skip, limit)

    @staticmethod
    def get_candidate(db: Session, candidate_id: int) -> schemas.Candidate:
        candidate = CandidateService.get_candidate(db, candidate_id)
        if candidate is None:
            raise HTTPException(status_code=404, detail="Candidate not found")
        return candidate

    @staticmethod
    def create_candidate(db: Session, candidate: schemas.CandidateCreate) -> schemas.Candidate:
        try:
            return CandidateService.create_candidate(db, candidate)
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e))

    @staticmethod
    def update_candidate(
        db: Session,
        candidate_id: int,
        candidate: schemas.CandidateBase
    ) -> schemas.Candidate:
        try:
            updated_candidate = CandidateService.update_candidate(db, candidate_id, candidate)
            if updated_candidate is None:
                raise HTTPException(status_code=404, detail="Candidate not found")
            return updated_candidate
        except ValueError as e:
            raise HTTPException(status_code=400, detail=str(e)) 