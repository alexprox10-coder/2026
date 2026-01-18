#!/usr/bin/env python3
"""
Get unsent listings and output as JSON for n8n
"""
import sys
import os
import json

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from database.models import init_db, get_unsent_listings

    db = init_db('rental_parser.db')
    listings = get_unsent_listings(db, limit=20)

    result = []
    for listing in listings:
        result.append({
            'id': listing.id,
            'platform': listing.platform,
            'listing_id': listing.listing_id,
            'url': listing.url,
            'title': listing.title or '',
            'price': listing.price,
            'phone': listing.phone,
            'address': listing.address or '',
            'rooms': listing.rooms,
            'area': listing.area
        })

    # Output JSON to stdout
    print(json.dumps(result, ensure_ascii=False))
    sys.exit(0)

except Exception as e:
    print(json.dumps({'error': str(e)}), file=sys.stderr)
    sys.exit(1)
