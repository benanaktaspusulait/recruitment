from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.base_entity import BaseEntity
from src.models.entities import User

T = TypeVar('T', bound=BaseEntity)

class BaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model

    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[T]:
        query = db.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, data: dict, current_user: User) -> T:
        db_item = self.model(**data)
        db_item.created_by_id = current_user.id
        db_item.updated_by_id = current_user.id
        
        try:
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            return db_item
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def update(
        self, 
        db: Session, 
        id: int, 
        data: dict,
        current_user: User
    ) -> Optional[T]:
        db_item = self.get_by_id(db, id)
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            db_item.updated_by_id = current_user.id
            
            try:
                db.commit()
                db.refresh(db_item)
                return db_item
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        return None

    def delete(self, db: Session, id: int) -> bool:
        db_item = self.get_by_id(db, id)
        if db_item:
            try:
                db.delete(db_item)
                db.commit()
                return True
            except Exception as e:
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        return False 