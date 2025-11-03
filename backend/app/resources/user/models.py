from sqlalchemy import Column, String, Boolean, Integer, Enum as SAEnum
from app.core.db import Base
import enum

class UserRole(enum.Enum):
    ATHLETE = "athlete"
    COACH = "coach"
    COORDINATOR = "coordinator"

class User(Base):
    __tablename__= "users"
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    full_name = Column(String, index=True)

    #Almacena la contraseña hasheada
    hashed_password = Column(String, nullable=False)

    #rol
    role = Column(
        SAEnum(UserRole),
        nullable=False,
        default=UserRole.ATHLETE
    )

    is_active = Column(Boolean, default=True)

    #Definir relaciones