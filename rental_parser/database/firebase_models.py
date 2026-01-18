"""
Firebase Firestore models for rental property parser
"""
from datetime import datetime
from typing import List, Dict, Optional
from google.cloud.firestore_v1 import FieldFilter
from .firebase_config import get_db


class RentalListingFirebase:
    """Model for rental property listings in Firestore"""

    COLLECTION = 'rental_listings'

    @staticmethod
    def create(listing_data: Dict) -> str:
        """
        Create new listing in Firestore

        Args:
            listing_data: Listing data dictionary

        Returns:
            Document ID
        """
        db = get_db()

        # Add timestamps
        listing_data['created_at'] = datetime.utcnow()
        listing_data['sent_to_manager'] = listing_data.get('sent_to_manager', False)
        listing_data['is_active'] = listing_data.get('is_active', True)
        listing_data['last_seen'] = datetime.utcnow()

        # Create document with listing_id as document ID
        doc_id = listing_data.get('listing_id')
        if not doc_id:
            raise ValueError("listing_id is required")

        doc_ref = db.collection(RentalListingFirebase.COLLECTION).document(doc_id)
        doc_ref.set(listing_data)

        return doc_id

    @staticmethod
    def exists(listing_id: str) -> bool:
        """Check if listing exists"""
        db = get_db()
        doc_ref = db.collection(RentalListingFirebase.COLLECTION).document(listing_id)
        return doc_ref.get().exists

    @staticmethod
    def update_last_seen(listing_id: str):
        """Update last_seen timestamp"""
        db = get_db()
        doc_ref = db.collection(RentalListingFirebase.COLLECTION).document(listing_id)
        doc_ref.update({
            'last_seen': datetime.utcnow()
        })

    @staticmethod
    def get_unsent(limit: int = 10) -> List[Dict]:
        """
        Get unsent listings

        Args:
            limit: Maximum number of listings to return

        Returns:
            List of listing dictionaries
        """
        db = get_db()

        # Query unsent, active listings
        query = db.collection(RentalListingFirebase.COLLECTION)\
            .where(filter=FieldFilter('sent_to_manager', '==', False))\
            .where(filter=FieldFilter('is_active', '==', True))\
            .order_by('created_at', direction='DESCENDING')\
            .limit(limit)

        docs = query.stream()

        listings = []
        for doc in docs:
            data = doc.to_dict()
            data['id'] = doc.id  # Add document ID
            listings.append(data)

        return listings

    @staticmethod
    def mark_as_sent(listing_id: str, manager_id: str = 'n8n_workflow') -> bool:
        """
        Mark listing as sent

        Args:
            listing_id: Listing ID
            manager_id: Manager who received the listing

        Returns:
            True if successful
        """
        db = get_db()
        doc_ref = db.collection(RentalListingFirebase.COLLECTION).document(listing_id)

        if not doc_ref.get().exists:
            return False

        doc_ref.update({
            'sent_to_manager': True,
            'sent_at': datetime.utcnow(),
            'manager_id': manager_id
        })

        return True

    @staticmethod
    def get_stats() -> Dict:
        """Get database statistics"""
        db = get_db()

        # Total count
        total_docs = db.collection(RentalListingFirebase.COLLECTION).stream()
        total = sum(1 for _ in total_docs)

        # Unsent count
        unsent_docs = db.collection(RentalListingFirebase.COLLECTION)\
            .where(filter=FieldFilter('sent_to_manager', '==', False))\
            .stream()
        unsent = sum(1 for _ in unsent_docs)

        # By platform
        by_platform = {}
        for platform in ['cian', 'yandex', 'avito']:
            platform_docs = db.collection(RentalListingFirebase.COLLECTION)\
                .where(filter=FieldFilter('platform', '==', platform))\
                .stream()
            by_platform[platform] = sum(1 for _ in platform_docs)

        return {
            'total': total,
            'unsent': unsent,
            'by_platform': by_platform
        }


class ParsingSessionFirebase:
    """Model for parsing sessions in Firestore"""

    COLLECTION = 'parsing_sessions'

    @staticmethod
    def create(platform: str) -> str:
        """Create new parsing session"""
        db = get_db()

        session_data = {
            'platform': platform,
            'started_at': datetime.utcnow(),
            'status': 'running',
            'listings_found': 0,
            'listings_new': 0
        }

        doc_ref = db.collection(ParsingSessionFirebase.COLLECTION).document()
        doc_ref.set(session_data)

        return doc_ref.id

    @staticmethod
    def update(session_id: str, data: Dict):
        """Update parsing session"""
        db = get_db()
        doc_ref = db.collection(ParsingSessionFirebase.COLLECTION).document(session_id)
        doc_ref.update(data)

    @staticmethod
    def complete(session_id: str, listings_found: int, listings_new: int):
        """Mark session as completed"""
        db = get_db()
        doc_ref = db.collection(ParsingSessionFirebase.COLLECTION).document(session_id)

        doc_ref.update({
            'completed_at': datetime.utcnow(),
            'status': 'completed',
            'listings_found': listings_found,
            'listings_new': listings_new
        })

    @staticmethod
    def fail(session_id: str, error_message: str):
        """Mark session as failed"""
        db = get_db()
        doc_ref = db.collection(ParsingSessionFirebase.COLLECTION).document(session_id)

        doc_ref.update({
            'completed_at': datetime.utcnow(),
            'status': 'failed',
            'error_message': error_message
        })


class ManagerFirebase:
    """Model for managers in Firestore"""

    COLLECTION = 'managers'

    @staticmethod
    def create(telegram_id: str, name: str) -> str:
        """Create new manager"""
        db = get_db()

        manager_data = {
            'telegram_id': telegram_id,
            'name': name,
            'is_active': True,
            'created_at': datetime.utcnow(),
            'city': None,
            'max_price': None,
            'min_rooms': None
        }

        doc_ref = db.collection(ManagerFirebase.COLLECTION).document(telegram_id)
        doc_ref.set(manager_data)

        return telegram_id

    @staticmethod
    def exists(telegram_id: str) -> bool:
        """Check if manager exists"""
        db = get_db()
        doc_ref = db.collection(ManagerFirebase.COLLECTION).document(telegram_id)
        return doc_ref.get().exists

    @staticmethod
    def get(telegram_id: str) -> Optional[Dict]:
        """Get manager by telegram_id"""
        db = get_db()
        doc_ref = db.collection(ManagerFirebase.COLLECTION).document(telegram_id)
        doc = doc_ref.get()

        if doc.exists:
            return doc.to_dict()
        return None
