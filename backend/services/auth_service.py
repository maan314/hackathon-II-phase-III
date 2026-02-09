from sqlmodel import Session, select
from models.user import User, UserCreate
from core.security import get_password_hash, verify_password
from typing import Optional
from datetime import datetime

def create_user(*, session: Session, user_create: UserCreate) -> User:
    """Create a new user in the database"""
    # Hash the password
    hashed_password = get_password_hash(user_create.password)

    # Create the user object
    db_user = User(
        email=user_create.email,
        first_name=user_create.first_name,
        last_name=user_create.last_name,
        hashed_password=hashed_password,
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )

    # Add to session and commit
    session.add(db_user)
    session.commit()
    session.refresh(db_user)

    return db_user

def authenticate_user(*, session: Session, email: str, password: str) -> Optional[User]:
    """Authenticate a user by email and password"""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()

    if not user:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user

def get_user_by_email(*, session: Session, email: str) -> Optional[User]:
    """Get a user by email"""
    statement = select(User).where(User.email == email)
    user = session.exec(statement).first()
    return user

def get_user_by_id(*, session: Session, user_id: int) -> Optional[User]:
    """Get a user by ID"""
    statement = select(User).where(User.id == user_id)
    user = session.exec(statement).first()
    return user