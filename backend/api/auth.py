from fastapi import APIRouter, Depends, HTTPException, status
from sqlmodel import Session, select
from models.user import UserCreate, UserLogin, UserResponse, User
from services.auth_service import create_user, authenticate_user
from core.security import create_access_token
from database import get_session
from datetime import timedelta
from typing import Dict, Any

router = APIRouter(prefix="/auth", tags=["auth"])

@router.post("/signup", response_model=Dict[str, Any])
def signup(user_create: UserCreate, session: Session = Depends(get_session)):
    """Register a new user"""
    # Check if user already exists
    existing_user = session.exec(select(User).where(User.email == user_create.email)).first()
    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="A user with this email already exists"
        )

    # Create the user
    db_user = create_user(session=session, user_create=user_create)

    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(db_user.id)}, expires_delta=access_token_expires
    )

    # Return user data with token
    user_response = UserResponse(
        id=db_user.id,
        email=db_user.email,
        first_name=db_user.first_name,
        last_name=db_user.last_name,
        created_at=db_user.created_at
    )

    return {"user": user_response, "token": access_token}


@router.post("/signin", response_model=Dict[str, Any])
def signin(user_login: UserLogin, session: Session = Depends(get_session)):
    """Authenticate a user and return JWT token"""
    user = authenticate_user(session=session, email=user_login.email, password=user_login.password)

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect email or password",
            headers={"WWW-Authenticate": "Bearer"},
        )

    # Create JWT token
    access_token_expires = timedelta(minutes=30)
    access_token = create_access_token(
        data={"sub": str(user.id)}, expires_delta=access_token_expires
    )

    # Return user data with token
    user_response = UserResponse(
        id=user.id,
        email=user.email,
        first_name=user.first_name,
        last_name=user.last_name,
        created_at=user.created_at
    )

    return {"user": user_response, "token": access_token}