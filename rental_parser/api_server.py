#!/usr/bin/env python3
"""
Simple Flask API for n8n integration
Run this server and n8n will call it via HTTP Request nodes
"""
from flask import Flask, jsonify, request
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import init_db, get_unsent_listings, mark_as_sent
from main import RentalParserOrchestrator

app = Flask(__name__)

# Initialize database
db = init_db('rental_parser.db')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok'})


@app.route('/parse', methods=['POST'])
def run_parser():
    """Run parser for all platforms"""
    try:
        data = request.get_json() or {}
        max_pages = data.get('max_pages', 5)

        orchestrator = RentalParserOrchestrator(city='москва', db_path='rental_parser.db')
        stats = orchestrator.parse_all(max_pages=max_pages)
        orchestrator.close()

        return jsonify({
            'success': True,
            'stats': stats
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/unsent', methods=['GET'])
def get_unsent():
    """Get unsent listings"""
    try:
        limit = int(request.args.get('limit', 20))
        listings = get_unsent_listings(db, limit=limit)

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

        return jsonify(result)
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/mark-sent/<int:listing_id>', methods=['POST'])
def mark_listing_sent(listing_id):
    """Mark listing as sent"""
    try:
        success = mark_as_sent(db, listing_id, 'n8n_workflow')

        if success:
            return jsonify({'success': True, 'listing_id': listing_id})
        else:
            return jsonify({'success': False, 'error': 'Listing not found'}), 404
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500


if __name__ == '__main__':
    print("Starting Rental Parser API...")
    print("API will be available at: http://localhost:5555")
    print("\nEndpoints:")
    print("  GET  /health - Health check")
    print("  POST /parse - Run parser")
    print("  GET  /unsent?limit=20 - Get unsent listings")
    print("  POST /mark-sent/<id> - Mark listing as sent")

    app.run(host='0.0.0.0', port=5555, debug=False)
