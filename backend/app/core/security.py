from datetime import datetime, timedelta, timezone
from typing import Any, Optional, List
from jose import JWTError, jwt
from passlib.context import CryptContext
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import settings
from app.db.database import get_db
from app.models.sqlalchemy import User

# Password hashing context - using pbkdf2_sha256 for better compatibility with Python 3.14
pwd_context = CryptContext(schemes=["pbkdf2_sha256", "bcrypt"], deprecated="auto")


# OAuth2 scheme for token extraction
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifies a plain password against its hash."""
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Generates a bcrypt hash for a password."""
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    """Creates a JWT access token."""
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=15)
    
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.jwt_secret_key, algorithm="HS256")
    return encoded_jwt

def decode_access_token(token: str) -> Optional[dict]:
    """
    Decodes and validates a JWT access token.
    Returns the payload if valid, otherwise returns None.
    """
    try:
        payload = jwt.decode(token, settings.jwt_secret_key, algorithms=["HS256"])
        return payload
    except JWTError:
        return None

async def get_current_user(
    db: Session = Depends(get_db),
    token: str = Depends(oauth2_scheme)
) -> User:
    """
    Dependency that extracts the user from the JWT token.
    Validates token integrity and user existence.
    """
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    payload = decode_access_token(token)
    if payload is None:
        raise credentials_exception
        
    email: str = payload.get("sub")
    if email is None:
        raise credentials_exception
    
    user = db.query(User).filter(User.email == email).first()
    if user is None:
        raise credentials_exception
    return user

class RoleChecker:
    """
    Dependency for Role-Based Access Control (RBAC).
    Checks if the current user has one of the allowed roles.
    """
    def __init__(self, allowed_roles: List[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: User = Depends(get_current_user)):
        if user.role not in self.allowed_roles:
            logger_info = f"User {user.email} with role {user.role} denied access. Allowed: {self.allowed_roles}"
            print(logger_info)
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="You do not have enough permissions to perform this action"
            )
        return user
