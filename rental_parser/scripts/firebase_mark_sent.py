#!/usr/bin/env python3
"""
Script to mark listing as sent in Firebase from n8n
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.firebase_config import init_firebase
from database.firebase_models import RentalListingFirebase

def main():
    if len(sys.argv) < 2:
        print("ERROR: Usage: firebase_mark_sent.py <listing_id>", file=sys.stderr)
        return 1

    listing_id = sys.argv[1]

    try:
        credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')
        init_firebase(credentials_path)

        success = RentalListingFirebase.mark_as_sent(listing_id, 'n8n_workflow')

        if success:
            print(f"SUCCESS: Marked listing {listing_id} as sent")
            return 0
        else:
            print(f"ERROR: Listing {listing_id} not found", file=sys.stderr)
            return 1
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    exit(main())
