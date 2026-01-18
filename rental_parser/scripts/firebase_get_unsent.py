#!/usr/bin/env python3
"""
Script to get unsent listings from Firebase for n8n
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.firebase_config import init_firebase
from database.firebase_models import RentalListingFirebase

def main():
    try:
        credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        init_firebase(credentials_path)

        listings = RentalListingFirebase.get_unsent(limit=20)

        output = []
        for listing in listings:
            output.append({
                'id': listing.get('id'),
                'platform': listing.get('platform'),
                'listing_id': listing.get('listing_id'),
                'url': listing.get('url'),
                'title': listing.get('title', ''),
                'price': listing.get('price'),
                'phone': listing.get('phone'),
                'address': listing.get('address', ''),
                'rooms': listing.get('rooms'),
                'area': listing.get('area')
            })

        print(json.dumps(output, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    exit(main())
