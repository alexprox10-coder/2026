"""
Firebase configuration and initialization
"""
import os
import firebase_admin
from firebase_admin import credentials, firestore
from typing import Optional

# Singleton instance
_db = None


def init_firebase(credentials_path: Optional[str] = None) -> firestore.Client:
    """
    Initialize Firebase connection

    Args:
        credentials_path: Path to Firebase service account JSON

    Returns:
        Firestore client instance
    """
    global _db

    if _db is not None:
        return _db

    # Get credentials path from env or parameter
    cred_path = credentials_path or os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

    try:
        # Initialize Firebase Admin SDK
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred)

        # Get Firestore client
        _db = firestore.client()
        return _db

    except Exception as e:
        raise Exception(f"Failed to initialize Firebase: {e}")


def get_db() -> firestore.Client:
    """Get existing Firestore client or create new one"""
    global _db
    if _db is None:
        _db = init_firebase()
    return _db
