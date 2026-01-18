#!/usr/bin/env python3
"""
Mark listing as sent
Usage: python3 n8n_mark_sent.py <listing_id>
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.models import init_db, mark_as_sent

    if len(sys.argv) < 2:
        print('ERROR: listing_id required', file=sys.stderr)
        sys.exit(1)

    listing_id = int(sys.argv[1])

    db = init_db('rental_parser.db')
    success = mark_as_sent(db, listing_id, 'n8n_workflow')

    if success:
        print(f'OK: Marked {listing_id} as sent')
        sys.exit(0)
    else:
        print(f'ERROR: Listing {listing_id} not found', file=sys.stderr)
        sys.exit(1)

except Exception as e:
    print(f'ERROR: {str(e)}', file=sys.stderr)
    sys.exit(1)
