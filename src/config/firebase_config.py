import os
import json
import threading
import firebase_admin
from firebase_admin import credentials, messaging, auth
from loguru import logger

_firebase_app = None
_init_lock = threading.Lock()

def initialize_firebase():
    """
    100% Stable 'Fresh Start' Firebase initialization.
    Prioritizes Local File (Robust) -> Individual ENV Keys (Safe).
    """
    global _firebase_app
    with _init_lock:
        try:
            # 1. Check if already initialized
            try:
                existing_app = firebase_admin.get_app()
                if existing_app:
                    _firebase_app = existing_app
                    return _firebase_app
            except ValueError:
                pass 

            # 2. PRIORITY: Native Cert Load (Most Stable)
            cert_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "service-account.json")
            if os.path.exists(cert_path):
                try:
                    cred = credentials.Certificate(cert_path)
                    _firebase_app = firebase_admin.initialize_app(cred)
                    logger.info(f"Firebase initialized via Stable File: {cert_path}")
                    return _firebase_app
                except Exception as e:
                    logger.warning(f"File init failed: {e}. Falling back to Individual ENV...")

            # 3. FALLBACK: Individual ENV Keys (Manual Re-Wrapping)
            config = {
                "type": "service_account",
                "project_id": os.getenv("FIREBASE_PROJECT_ID"),
                "private_key_id": os.getenv("FIREBASE_PRIVATE_KEY_ID"),
                "private_key": os.getenv("FIREBASE_PRIVATE_KEY"),
                "client_email": os.getenv("FIREBASE_CLIENT_EMAIL"),
                "client_id": os.getenv("FIREBASE_CLIENT_ID"),
                "auth_uri": "https://accounts.google.com/o/oauth2/auth",
                "token_uri": "https://oauth2.googleapis.com/token",
                "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
                "client_x509_cert_url": os.getenv("FIREBASE_CLIENT_CERT_URL")
            }

            if config["private_key"]:
                import re
                pk = str(config["private_key"])
                pk_clean = re.sub(r'-----BEGIN PRIVATE KEY-----|-----END PRIVATE KEY-----|[\s\\n]', '', pk).strip()
                
                # Force standard 64-char wrapping for strict OpenSSL compatibility
                chunks = [pk_clean[i:i+64] for i in range(0, len(pk_clean), 64)]
                pk_wrapped = "\n".join(chunks)
                config["private_key"] = f"-----BEGIN PRIVATE KEY-----\n{pk_wrapped}\n-----END PRIVATE KEY-----\n"

                try:
                    cred = credentials.Certificate(config)
                    _firebase_app = firebase_admin.initialize_app(cred)
                    logger.info("Firebase initialized via Strict-Wrapped ENV Keys.")
                    return _firebase_app
                except Exception as e:
                    logger.error(f"ENV initialization FAILED: {e}")

            # 4. FINAL FALLBACK: Default Credentials
            _firebase_app = firebase_admin.initialize_app()
            logger.info("Firebase initialized via Default Credentials Fallback.")
            return _firebase_app
            
        except Exception as e:
            logger.error(f"CRITICAL: All Firebase init paths failed: {e}")
            return None

def verify_token(id_token: str):
    """
    Verify a Firebase ID token.
    """
    try:
        # Ensure initialized
        initialize_firebase()
        project_id = os.getenv("FIREBASE_PROJECT_ID")
        # Guarantee project ID is in environment for the SDK's internal lookups
        if project_id and not os.environ.get("GOOGLE_CLOUD_PROJECT"):
            os.environ["GOOGLE_CLOUD_PROJECT"] = project_id
            os.environ["FIREBASE_PROJECT_ID"] = project_id

        # Pass the explicit app instance to verify_id_token
        decoded_token = auth.verify_id_token(id_token, app=_firebase_app)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None

def get_messaging():
    return messaging

def get_auth():
    return auth
