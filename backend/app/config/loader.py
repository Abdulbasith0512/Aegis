import logging
import sys
from app.config.settings import Settings

logger = logging.getLogger("aegisai.config")

def load_settings() -> Settings:
    """
    Safely loads and validates configuration settings.
    Applies security assertions for production environments.
    Returns:
        Settings: Validated configuration object.
    """
    try:
        validated_settings = Settings()
        
        # Security Assertions for Production environments
        if validated_settings.ENVIRONMENT == "production":
            # 1. Require a strong secret key
            if (
                not validated_settings.SECRET_KEY 
                or validated_settings.SECRET_KEY == "aegisai_default_secret_key_change_me_in_production_environments_32_chars" 
                or len(validated_settings.SECRET_KEY) < 32
            ):
                logger.critical("Insecure SECRET_KEY set for production environment! Exiting.")
                sys.exit(1)
            
            # 2. Assert database uses asyncpg driver
            if not validated_settings.DATABASE_URL.startswith("postgresql+asyncpg://"):
                logger.critical("Production DATABASE_URL must utilize the postgresql+asyncpg driver. Exiting.")
                sys.exit(1)
                
            # 3. Warn if logging level is too verbose
            if validated_settings.LOG_LEVEL.upper() == "DEBUG":
                logger.warning("Verbose DEBUG logging enabled in production mode.")
                
        return validated_settings

    except Exception as e:
        logger.critical(f"Failed to load or validate application settings: {e}")
        sys.exit(1)

# Single global instance of validated settings
settings: Settings = load_settings()
