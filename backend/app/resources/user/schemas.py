from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from .models import UserRole

class UserBase(BaseModel):
    email: EmailStr
    full_name: Optional[str] = None

class UserCreate(UserBase):
    password: str = Field(
        ...,
        min_length=8,
        max_length=72
    )
    role: UserRole = UserRole.ATHLETE #por default

class UserUpdate(BaseModel):
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    password: Optional[str] = None #Para permitir cambiar la contraseña
    role: Optional[UserRole] = None
    is_active: Optional [bool] = None

#Esquema de lectura
class User(UserBase):
    id: int
    role: UserRole
    is_active: bool

    class Config:
        from_attributes = True