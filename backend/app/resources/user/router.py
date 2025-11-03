from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from typing import List
from app.core.db import get_db_session
from . import schemas, service
from app.resources.auth.service import get_current_user
from . import models as user_models

router = APIRouter(
    prefix="/users",
    tags=["Users"] # Agrupa los endpoints en la documentación
)

# CREAR un usuario (POST /users/)
@router.post(
    "/",
    response_model=schemas.User, # El schema de respuesta
    status_code=status.HTTP_201_CREATED # Código 201 para "Creado"
)
async def create_user_endpoint(
    user_in: schemas.UserCreate, # El schema de entrada (body)
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para crear un nuevo usuario.
    """
    # Verificamos si el email ya existe
    db_user = await service.get_user_by_email(db, email=user_in.email)
    if db_user:
        # Si existe, lanzamos un error HTTP 400
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El email ya está registrado."
        )
    
    # Si no existe, llamamos al servicio para crear el usuario
    new_user = await service.create_user(db=db, user_data=user_in)
    return new_user

# OBTENER una lista de usuarios (GET /users/)
@router.get(
    "/",
    response_model=List[schemas.User] # Respuesta es una Lista de Users
)
async def read_users_endpoint(
    skip: int = 0, 
    limit: int = 100,
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para obtener una lista paginada de usuarios.
    """
    users = await service.get_users(db, skip=skip, limit=limit)
    return users


#Endpoint protegido para OBTENER el usuario "propio"
@router.get(
    "/me",
    response_model=schemas.User
)
async def read_users_me(
    #FastAPI ejecutará get_current_user,
    #verificará el token y devuelve el 'user_models.User'
    current_user: user_models.User = Depends(get_current_user)
):
    """
    Endpoint protegido para obtener los datos del usuario 
    actualmente autenticado (basado en el token JWT).
    """
    # Como la dependencia ya nos dio el usuario,
    # lo devolvemos.
    return current_user

# OBTENER un usuario por ID (GET /users/{user_id})
@router.get(
    "/{user_id}",
    response_model=schemas.User
)
async def read_user_endpoint(
    user_id: int, # Parámetro de la URL
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para obtener un usuario por su ID.
    """
    db_user = await service.get_user(db, user_id=user_id)
    if db_user is None:
        # Si no se encuentra, lanzamos un error HTTP 404
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado."
        )
    return db_user