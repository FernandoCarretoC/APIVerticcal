from pydantic_settings import BaseSettings
from functools import lru_cache

class Settings(BaseSettings):
    """Configuración de la aplicación"""

    # Configuración de Pipedrive
    PIPEDRIVE_API_TOKEN: str
    PIPEDRIVE_API_URL: str = "https://api.pipedrive.com/v1"

    # Configuración de la aplicación
    APP_ENV: str = "development"
    DEBUG: bool = True

    # Configuración de tiempo de espera y reintentos
    REQUEST_TIMEOUT: int = 30
    MAX_RETRIES: int = 3

    class Config:
        env_file = ".env"
        case_sensitive = True

@lru_cache()
def get_settings() -> Settings:
    """Obtiene la configuración de la aplicación con caché"""
    return Settings()

settings = get_settings()