from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker, AsyncSession
from sqlalchemy.orm import DeclarativeBase
from .config import settings
from typing import AsyncGenerator

# 1. Crear el Engine asíncrono
# Es el "punto de entrada" a nuestra base de datos.
# echo=True es útil para desarrollo, imprimirá las queries SQL que se ejecuten.
engine = create_async_engine(
    settings.DATABASE_URL,
    # connect_args es específico para SQLite, previene errores de concurrencia.
    connect_args={"check_same_thread": False}, 
    echo=True 
)

# 2. Crear la fábrica de sesiones (Session factory)
# Esto crea una *plantilla* para las sesiones de base de datos.
# No creamos una sesión aquí, solo la plantilla.
SessionLocal = async_sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False # No expira los datos después de un commit
)

# 3. Crear la Base declarativa
# Todos nuestros modelos (tablas) de SQLAlchemy heredarán de esta clase.
class Base(DeclarativeBase):
    pass


# --- Dependencia de FastAPI para obtener la sesión ---

async def get_db_session() -> AsyncGenerator[AsyncSession, None]:
    """
    Dependencia de FastAPI para inyectar una sesión de base de datos
    en los endpoints de la API.
    
    Usará 'yield' para:
    1. Crear una sesión (db) antes de que se ejecute el endpoint.
    2. Entregar (yield) esa sesión al endpoint.
    3. Asegurarse de cerrar (db.close()) la sesión al finalizar,
       incluso si ocurre un error.
    """
    async with SessionLocal() as session:
        try:
            yield session
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()