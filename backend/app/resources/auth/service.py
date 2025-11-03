from sqlalchemy.ext.asyncio import AsyncSession
from typing import Optional
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.core.config import settings #(para la SECRET_KEY)
from app.resources.user import service as user_service
from app.resources.user import models as user_models
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from app.core.db import get_db_session
from . import schemas as auth_schemas
from app.resources.user import schemas as user_schemas

async def authenticate_user(
    db: AsyncSession, 
    email: str, 
    password: str
) -> Optional[user_models.User]:
    """
    Verifica si un usuario existe y la contraseña es correcta.
    """
    # 1. Busca al usuario por email
    user = await user_service.get_user_by_email(db, email=email)
    
    if not user:
        return None # Usuario no encontrado
    
    # 2. Verifica la contraseña
    if not user_service.verify_password(password, user.hashed_password):
        return None # Contraseña incorrecta
        
    return user


def create_access_token(data: dict) -> str:
    """
    Crea un nuevo token JWT.
    """
    to_encode = data.copy()
    
    # 3. Define el tiempo de expiración del token
    expire = datetime.now(timezone.utc) + timedelta(
        minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
    )
    to_encode.update({"exp": expire})
    
    # 4. "Firma" el token con nuestra llave secreta
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


# "vigila" la URL /api/v1/auth/token
# para la autenticación (aunque no la usará directamente, es 
# necesario para la documentación de Swagger).
oauth2_scheme = OAuth2PasswordBearer(
    tokenUrl=f"{settings.API_V1_PREFIX}/auth/token"
)

async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db_session)
) -> user_models.User:
    """
    Dependencia para obtener el usuario actual a partir de un token JWT.
    
    1. Decodifica el token.
    2. Valida el email (subject).
    3. Busca al usuario en la DB.
    """
    
    #error estándar por si algo falla
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="No se pudieron validar las credenciales",
        headers={"WWW-Authenticate": "Bearer"},
    )
    
    try:
        #Decodificar el JWT
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        
        #Extraer el email del 'subject' (sub)
        email: str = payload.get("sub")
        if email is None:
            raise credentials_exception
            
        #Validar el schema de los datos del token
        token_data = auth_schemas.TokenData(email=email)
        
    except JWTError:
        #Si el token está malformado o expiró
        raise credentials_exception
        
    #Buscar al usuario en la base de datos
    user = await user_service.get_user_by_email(db, email=token_data.email)
    if user is None:
        raise credentials_exception
        
    #Devolver el modelo del usuario
    return user