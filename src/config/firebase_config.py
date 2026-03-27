import os
import firebase_admin
from firebase_admin import credentials, messaging, auth
from loguru import logger

def initialize_firebase():
    """
    Initialize Firebase Admin SDK idempotently.
    """
    try:
        # Check if initialized already
        try:
            firebase_admin.get_app()
            logger.info("Firebase already initialized.")
            return
        except ValueError:
            pass # Not initialized, proceed
            
        if not firebase_admin._apps:
            # 1. Try JSON string from ENV (for Cloud/Render)
            service_account_json = os.getenv("FIREBASE_SERVICE_ACCOUNT_JSON")
            if service_account_json:
                import json
                try:
                    cred_dict = json.loads(service_account_json)
                    cred = credentials.Certificate(cred_dict)
                    firebase_admin.initialize_app(cred)
                    logger.info("Firebase Admin SDK initialized using JSON string from environment.")
                    return
                except Exception as ex:
                    logger.error(f"Failed to load Firebase credentials from JSON string: {ex}")

            # 2. Try file path from env
            service_account_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH")
            if service_account_path and os.path.exists(service_account_path):
                cred = credentials.Certificate(service_account_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized with service account file.")
                return

            # 3. Fallback to local 'service-account.json' file
            default_path = "service-account.json"
            if os.path.exists(default_path):
                cred = credentials.Certificate(default_path)
                firebase_admin.initialize_app(cred)
                logger.info("Firebase Admin SDK initialized with local 'service-account.json'.")
                return

            # Ensure GOOGLE_CLOUD_PROJECT is set for Firebase Admin
            if not os.getenv("GOOGLE_CLOUD_PROJECT") and os.getenv("FIREBASE_PROJECT_ID"):
                os.environ["GOOGLE_CLOUD_PROJECT"] = os.getenv("FIREBASE_PROJECT_ID")

            # 4. Fallback to default credentials
            firebase_admin.initialize_app()
            logger.info(f"Firebase Admin SDK initialized with default credentials for project: {os.getenv('GOOGLE_CLOUD_PROJECT')}")
    except Exception as e:
        logger.error(f"Failed to initialize Firebase: {e}")

def verify_token(id_token: str):
    """Verify Firebase ID Token from frontend."""
    try:
        # Add 10 seconds of clock skew leeway to handle "Token used too early" errors
        decoded_token = auth.verify_id_token(id_token, clock_skew_seconds=10)
        return decoded_token
    except Exception as e:
        logger.error(f"Token verification failed: {e}")
        return None
