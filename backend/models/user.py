from sqlmodel import SQLModel, Field, Relationship
from typing import Optional, List
from datetime import datetime
import bcrypt
from pydantic import BaseModel

class UserBase(SQLModel):
    email: str = Field(unique=True, index=True)
    first_name: str
    last_name: str

class User(UserBase, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    hashed_password: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    # Relationship to todos
    todos: List["Todo"] = Relationship(back_populates="user")

    def verify_password(self, plain_password: str) -> bool:
        # Truncate password to 72 bytes to comply with bcrypt limitations
        truncated_password = plain_password[:72] if len(plain_password.encode('utf-8')) > 72 else plain_password
        return bcrypt.checkpw(truncated_password.encode('utf-8'), self.hashed_password.encode('utf-8'))

class UserCreate(UserBase):
    password: str

class UserRead(UserBase):
    id: int
    created_at: datetime

class UserLogin(BaseModel):
    email: str
    password: str

class UserResponse(BaseModel):
    id: int
    email: str
    first_name: str
    last_name: str
    created_at: datetime