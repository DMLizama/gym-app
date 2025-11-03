from pydantic import BaseModel
from typing import Optional

class Token(BaseModel):
    """
    Schema de respuesta para el token JWT.
    """
    access_token: str
    token_type: str


class TokenData(BaseModel):
    """
    Schema de los datos contenidos dentro del JWT.
    """
    email: Optional[str] = None
    # (Más adelante podríamos añadir 'scopes' o roles aquí)