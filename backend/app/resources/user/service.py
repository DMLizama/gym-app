from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from typing import List, Optional
from passlib.context import CryptContext #Para hashear passwords
from . import models, schemas

# 1. Configuración del Hashing de Contraseñas
# Le decimos a passlib que use 'bcrypt' como algoritmo
pwd_context = CryptContext(
    schemes=["bcrypt_sha256", "bcrypt"],  # acepta ambos (útil si ya tenés hashes viejos en bcrypt "puro")
    deprecated="auto",
)

def get_password_hash(password: str) -> str:
    """Genera el hash de una contraseña en texto plano."""
    return pwd_context.hash(password)

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verifica si la contraseña en texto plano coincide con el hash."""
    return pwd_context.verify(plain_password, hashed_password)

# Funciones CRUD

async def get_user(db: AsyncSession, user_id: int) -> Optional[models.User]:
    """Obtiene un usuario por su ID."""
    query = select(models.User).where(models.User.id == user_id)
    result = await db.execute(query)

    # .scalar_one_or_none() devuelvo un solo obj o None si no lo encuentra
    return result.scalar_one_or_none()

async def get_user_by_email(db: AsyncSession, email: str) -> Optional[models.User]:
    """Obtiene un usuario por su email."""
    query = select(models.User).where(models.User.email == email)
    result = await db.execute(query)
    return result.scalar_one_or_none()

async def get_users(db: AsyncSession, skip: int = 0, limit: int = 100) -> List[models.User]:
    """Obtiene una lista paginada de usuarios."""
    query = select(models.User).offset(skip).limit(limit)
    result = await db.execute(query)
    # .scalars().all() devuelve una lista de todos los resultados
    return result.scalars().all()

async def create_user(db: AsyncSession, user_data: schemas.UserCreate) -> models.User:
    """Crea un nuevo usuario en la base de datos."""
    #Hashear la contraseña
    hashed_password = get_password_hash(user_data.password)
    
    # Convertir el schema (Pydantic) a datos para el modelo (SQLAlchemy)
    # Usamos .model_dump() (en Pydantic v2) para obtener un dict
    # Excluimos 'password' porque no queremos guardar el texto plano
    user_model_data = user_data.model_dump(exclude={"password"})

    # Crear el objeto del modelo SQLAlchemy
    db_user = models.User(
        **user_model_data,
        hashed_password=hashed_password # Añadimos la contraseña hasheada
    )
    
    # 4. Añadir a la sesión de la DB y guardar
    db.add(db_user)
    await db.commit()
    
    # 5. Refrescar el objeto para obtener el ID generado por la DB
    await db.refresh(db_user)
    
    return db_user

# (Más adelante añadiremos 'update_user' y 'delete_user' aquí)