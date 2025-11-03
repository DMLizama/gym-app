from fastapi import FastAPI
from contextlib import asynccontextmanager #para el lifespan

#config y bd
from app.core.config import settings
from app.core.db import engine, Base

#routers de recursos
from app.resources.user.router import router as user_router
from app.resources.auth.router import router as auth_router

# --- Función para crear las tablas ---
async def create_db_and_tables():
    async with engine.begin() as conn:
        # 'run_sync' ejecuta la creación de tablas (que es síncrona)
        # de forma asíncrona, compatible con nuestro engine.
        await conn.run_sync(Base.metadata.create_all)

# --- Evento 'Lifespan' de FastAPI ---
# Esta es la forma moderna (en lugar de @app.on_event)
# de ejecutar código al iniciar y apagar la app.
@asynccontextmanager
async def lifespan(app: FastAPI):
    # --- Código al Iniciar (Startup) ---
    print("Iniciando la aplicación...")
    await create_db_and_tables()
    print("Tablas de la base de datos creadas.")
    
    yield # Aquí es donde la aplicación se ejecuta
    
    # --- Código al Apagar (Shutdown) ---
    print("Cerrando la aplicación...")
    # (Aquí podríamos cerrar conexiones si fuera necesario)


# --- Creación de la App ---
app = FastAPI(
    title="Gym App API",
    description="API para gestionar atletas, entrenadores y clases.",
    version="0.1.0",
    lifespan=lifespan # ¡Conectamos nuestro lifespan!
)

@app.get("/")
def read_root():
    return {"message": "¡Bienvenido a la API de Gym App!"}

#include de los routers
app.include_router(user_router, prefix=settings.API_V1_PREFIX) #bajo /api/v1
app.include_router(auth_router, prefix=settings.API_V1_PREFIX)