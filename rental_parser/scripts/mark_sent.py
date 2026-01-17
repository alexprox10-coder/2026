#!/usr/bin/env python3
"""
Script to mark listing as sent from n8n
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, mark_as_sent

def main():
    if len(sys.argv) < 2:
        print("ERROR: Usage: mark_sent.py <listing_id>", file=sys.stderr)
        return 1

    listing_id = int(sys.argv[1])

    try:
        db = init_db('rental_parser.db')
        success = mark_as_sent(db, listing_id, 'n8n_workflow')

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
