from loguru import logger
from typing import TypeVar, Generic, Type, List, Optional
from sqlalchemy.orm import Session
from fastapi import HTTPException
from src.models.base_entity import BaseEntity
from src.models.entities import User

T = TypeVar('T', bound=BaseEntity)

class BaseService(Generic[T]):
    def __init__(self, model: Type[T]):
        self.model = model
        self.logger = logger.bind(service=self.__class__.__name__)

    def get_all(
        self, 
        db: Session, 
        skip: int = 0, 
        limit: int = 100,
        **filters
    ) -> List[T]:
        self.logger.debug(f"Getting all {self.model.__name__} with filters: {filters}")
        query = db.query(self.model)
        for key, value in filters.items():
            if value is not None:
                query = query.filter(getattr(self.model, key) == value)
        return query.offset(skip).limit(limit).all()

    def get_by_id(self, db: Session, id: int) -> Optional[T]:
        self.logger.debug(f"Getting {self.model.__name__} with id: {id}")
        return db.query(self.model).filter(self.model.id == id).first()

    def create(self, db: Session, data: dict, current_user: User) -> T:
        self.logger.info(
            f"Creating new {self.model.__name__} by user {current_user.email}"
        )
        db_item = self.model(**data)
        db_item.created_by_id = current_user.id
        db_item.updated_by_id = current_user.id
        
        try:
            db.add(db_item)
            db.commit()
            db.refresh(db_item)
            self.logger.info(f"Created {self.model.__name__} with id: {db_item.id}")
            return db_item
        except Exception as e:
            self.logger.error(f"Error creating {self.model.__name__}: {str(e)}")
            db.rollback()
            raise HTTPException(status_code=400, detail=str(e))

    def update(
        self, 
        db: Session, 
        id: int, 
        data: dict,
        current_user: User
    ) -> Optional[T]:
        self.logger.info(
            f"Updating {self.model.__name__} id: {id} by user {current_user.email}"
        )
        db_item = self.get_by_id(db, id)
        if db_item:
            for key, value in data.items():
                setattr(db_item, key, value)
            db_item.updated_by_id = current_user.id
            
            try:
                db.commit()
                db.refresh(db_item)
                self.logger.info(f"Updated {self.model.__name__} id: {id}")
                return db_item
            except Exception as e:
                self.logger.error(f"Error updating {self.model.__name__} id {id}: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        return None

    def delete(self, db: Session, id: int) -> bool:
        self.logger.info(f"Deleting {self.model.__name__} id: {id}")
        db_item = self.get_by_id(db, id)
        if db_item:
            try:
                db.delete(db_item)
                db.commit()
                self.logger.info(f"Deleted {self.model.__name__} id: {id}")
                return True
            except Exception as e:
                self.logger.error(f"Error deleting {self.model.__name__} id {id}: {str(e)}")
                db.rollback()
                raise HTTPException(status_code=400, detail=str(e))
        return False 