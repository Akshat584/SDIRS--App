import re
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session
from datetime import timedelta
from pydantic import BaseModel, EmailStr, ConfigDict, field_validator

from app.db.database import get_db
from app.models.sqlalchemy import User
from app.core.security import verify_password, get_password_hash, create_access_token, get_current_user
from app.core.limiter import limiter

router = APIRouter()

class UserCreate(BaseModel):
    name: str
    email: EmailStr
    password: str
    phone_number: str | None = None
    role: str = "citizen" # 'citizen', 'responder'

    @field_validator('password')
    @classmethod
    def validate_password_strength(cls, v):
        if len(v) < 8:
            raise ValueError('Password must be at least 8 characters long')
        if not re.search(r'[A-Z]', v):
            raise ValueError('Password must contain at least one uppercase letter')
        if not re.search(r'[a-z]', v):
            raise ValueError('Password must contain at least one lowercase letter')
        if not re.search(r'[0-9]', v):
            raise ValueError('Password must contain at least one number')
        if not re.search(r'[!@#$%^&*(),.?":{}|<>]', v):
            raise ValueError('Password must contain at least one special character')
        return v

class TokenResponse(BaseModel):
    access_token: str
    token_type: str
    role: str

@router.post("/register", status_code=status.HTTP_201_CREATED)
@limiter.limit("5/minute")
def register_user(request: Request, user_data: UserCreate, db: Session = Depends(get_db)):
    """Registers a new user (Citizen or Responder)."""
    # Check if user already exists
    if db.query(User).filter(User.email == user_data.email).first():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists."
        )
    
    new_user = User(
        name=user_data.name,
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        phone_number=user_data.phone_number,
        role=user_data.role,
        status="active"
    )
    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return {"message": "User registered successfully", "user_id": new_user.id}

@router.post("/login", response_model=TokenResponse)
@limiter.limit("10/minute")
def login_for_access_token(
    request: Request,
    db: Session = Depends(get_db),
    form_data: OAuth2PasswordRequestForm = Depends()
):
    """Authenticated login that returns a JWT token with account lockout protection."""
    user = db.query(User).filter(User.email == form_data.username).first()
    
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Check if account is locked
    if user.is_locked:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Account is locked due to too many failed attempts. Please contact support."
        )

    if not verify_password(form_data.password, user.hashed_password):
        # Increment failed attempts
        user.failed_login_attempts += 1
        if user.failed_login_attempts >= 5:
            user.is_locked = True
        db.commit()
        
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Reset failed attempts on success
    user.failed_login_attempts = 0
    db.commit()
    
    access_token = create_access_token(data={"sub": user.email, "role": user.role})
    return {
        "access_token": access_token, 
        "token_type": "bearer",
        "role": user.role
    }

class UserProfile(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    name: str
    email: EmailStr
    phone_number: str | None = None
    role: str
    status: str

@router.get("/me", response_model=UserProfile)
def read_users_me(current_user: User = Depends(get_current_user)):
    """Returns the profile of the currently logged-in user."""
    return current_user
