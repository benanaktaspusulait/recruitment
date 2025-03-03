from sqlalchemy import Column, Integer, DateTime, String, ForeignKey
from sqlalchemy.orm import declared_attr
from src.database import Base
from datetime import datetime, UTC

class BaseEntity:
    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))
    
    @declared_attr
    def created_by_id(cls):
        return Column(Integer, ForeignKey("users.id"))
    
    @declared_attr
    def updated_by_id(cls):
        return Column(Integer, ForeignKey("users.id")) 