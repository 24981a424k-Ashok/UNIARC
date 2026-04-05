import os
import logging
from typing import Optional
from src.database.database import SessionLocal
from src.database.models import SystemSecret

logger = logging.getLogger(__name__)

class SecretManager:
    """
    Manages application secrets by fetching from PostgreSQL first, 
    then falling back to environment variables.
    Includes a simple local cache to minimize DB roundtrips.
    """
    _cache = {}

    @classmethod
    def get(cls, key: str, default: Optional[str] = None) -> Optional[str]:
        # 1. Check Local Cache
        if key in cls._cache:
            return cls._cache[key]

        # 2. Check Database
        db = SessionLocal()
        try:
            secret = db.query(SystemSecret).filter(SystemSecret.key == key).first()
            if secret:
                cls._cache[key] = secret.value
                return secret.value
        except Exception as e:
            logger.warning(f"Could not fetch secret {key} from database: {e}")
        finally:
            db.close()

        # 3. Fallback to Environment Variable
        env_val = os.getenv(key)
        if env_val:
            # We don't cache env vars permanently to allow for DB overrides later
            return env_val

        return default

    @classmethod
    def set(cls, key: str, value: str, description: Optional[str] = None):
        """Helper to update a secret in the DB (for migration/admin)"""
        db = SessionLocal()
        try:
            secret = db.query(SystemSecret).filter(SystemSecret.key == key).first()
            if secret:
                secret.value = value
                secret.description = description or secret.description
            else:
                secret = SystemSecret(key=key, value=value, description=description)
                db.add(secret)
            db.commit()
            cls._cache[key] = value # Update cache
            logger.info(f"Secret updated in DB: {key}")
        except Exception as e:
            db.rollback()
            logger.error(f"Failed to set secret {key}: {e}")
        finally:
            db.close()

    @classmethod
    def clear_cache(cls):
        cls._cache = {}
