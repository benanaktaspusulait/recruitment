from datetime import datetime, timedelta, UTC
from typing import Optional
from jose import JWTError, jwt
from sqlalchemy.orm import Session
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from src.models import schemas, entities
from src.database import get_db

# Configuration (move to settings later)
SECRET_KEY = "your-secret-key"  # Change this!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="v1/auth/token")

class AuthService:
    @staticmethod
    def create_user(db: Session, user_create: schemas.UserCreate) -> entities.User:
        # Check if user exists
        if db.query(entities.User).filter(entities.User.email == user_create.email).first():
            raise ValueError("Email already registered")

        # Create user
        db_user = entities.User(
            email=user_create.email,
            hashed_password=entities.User.hash_password(user_create.password.get_secret_value()),
            role=user_create.role
        )
        db.add(db_user)

        # If role is candidate, create candidate profile
        if user_create.role == entities.UserRole.CANDIDATE:
            if not all([user_create.first_name, user_create.last_name]):
                raise ValueError("First name and last name are required for candidates")
            
            db_candidate = entities.Candidate(
                user=db_user,
                email=user_create.email,
                first_name=user_create.first_name,
                last_name=user_create.last_name,
                phone=user_create.phone
            )
            db.add(db_candidate)

        try:
            db.commit()
            db.refresh(db_user)
            return db_user
        except Exception as e:
            db.rollback()
            raise ValueError(f"Failed to create user: {str(e)}")

    @staticmethod
    def authenticate_user(db: Session, email: str, password: str) -> Optional[entities.User]:
        user = db.query(entities.User).filter(entities.User.email == email).first()
        if not user or not user.verify_password(password):
            return None
        return user

    @staticmethod
    def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.now(UTC) + expires_delta
        else:
            expire = datetime.now(UTC) + timedelta(minutes=15)
        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
        return encoded_jwt

    @staticmethod
    async def get_current_user(
        db: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme)
    ) -> entities.User:
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            email: str = payload.get("sub")
            if email is None:
                raise credentials_exception
        except JWTError:
            raise credentials_exception

        user = db.query(entities.User).filter(entities.User.email == email).first()
        if user is None:
            raise credentials_exception
        return user

    @staticmethod
    def get_current_active_user(
        current_user: entities.User = Depends(get_current_user)
    ) -> entities.User:
        if not current_user.is_active:
            raise HTTPException(status_code=400, detail="Inactive user")
        return current_user 