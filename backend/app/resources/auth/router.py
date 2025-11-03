from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.db import get_db_session
from . import service as auth_service
from . import schemas

router = APIRouter(
    prefix="/auth",
    tags=["Auth"] # Lo agrupamos en "Auth" en los /docs
)

@router.post(
    "/token", 
    response_model=schemas.Token
)
async def login_for_access_token(
    # 1. Dependencia clave:
    # FastAPI buscará campos 'username' y 'password' 
    # en los datos de un formulario (no en un JSON).
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: AsyncSession = Depends(get_db_session)
):
    """
    Endpoint para iniciar sesión y obtener un token JWT.
    El 'username' del formulario se tratará como el 'email'.
    """
    
    # 2. Autenticamos al usuario
    # Pasamos el 'form_data.username' como el 'email'
    user = await auth_service.authenticate_user(
        db, 
        email=form_data.username, 
        password=form_data.password
    )
    
    # 3. Si falla la autenticación, lanzamos un error 401
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Email o contraseña incorrectos",
            # Esto es estándar para los errores de login
            headers={"WWW-Authenticate": "Bearer"},
        )
        
    # 4. Si tiene éxito, creamos el token
    # El 'subject' (sub) del token será el email del usuario
    access_token = auth_service.create_access_token(
        data={"sub": user.email}
    )
    
    # 5. Devolvemos el token
    return {"access_token": access_token, "token_type": "bearer"}