from pydantic_settings import BaseSettings, SettingsConfigDict
import os

# Define la ruta absoluta al directorio 'backend'
# __file__ es 'backend/app/core/config.py'
# .parent es 'backend/app/core'
# .parent.parent es 'backend/app'
# .parent.parent.parent es 'backend'
BACKEND_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

class Settings(BaseSettings):
    """
    Configuración global de la aplicación, leída desde variables de entorno y/o un archivo .env.
    """

    # Carga las variable desde un archivo .env ubicado en la raíz de 'backend'
    model_config = SettingsConfigDict(
        env_file=os.path.join(BACKEND_DIR, '.env'),
        env_file_encoding='utf-8',
        extra='ignore' # Para ignorar variables extra en el .env
    )

    # --- Configuración de la Base de Datos ---
    # SQLite asíncrona por defecto.
    # 'sqlite+aiosqlite:///./gym.db' crea un archivo 'gym.db' 
    # en la raíz del directorio 'backend' (donde ejecuto uvicorn).
    DATABASE_URL: str = f"sqlite+aiosqlite:///{os.path.join(BACKEND_DIR, 'gym.db')}"

    # --- Configuración de la API ---
    API_V1_PREFIX: str = "/api/v1"

    # --- Configuración de Seguridad (para JWT - Login) ---
    # ¡Cambiar esto en producción!
    # Puedes generar uno con: openssl rand -hex 32
    SECRET_KEY: str = "09d25e094faa6ca2556c818166b7a9563b93f7099f6f0f4caa6cf63b88e8d3e7"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 # 1 día

# Creamos una instancia única que será importada por el resto de la app
settings = Settings()