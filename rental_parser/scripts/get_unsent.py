#!/usr/bin/env python3
"""
Script to get unsent listings as JSON for n8n
"""
import sys
import os
import json

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, get_unsent_listings

def main():
    try:
        db = init_db('rental_parser.db')
        listings = get_unsent_listings(db, limit=20)

        output = []
        for listing in listings:
            output.append({
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

        print(json.dumps(output, ensure_ascii=False))
        return 0
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1

if __name__ == '__main__':
    exit(main())
