#!/usr/bin/env python3
"""
Simple Flask API for n8n integration
Run this server and n8n will call it via HTTP Request nodes
"""
from flask import Flask, jsonify, request
import subprocess
import sys
import os
import json

app = Flask(__name__)

# Path to run_once.py script
SCRIPT_PATH = os.path.join(os.path.dirname(__file__), 'run_once.py')


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'ok', 'message': 'API server is running'})


@app.route('/parse', methods=['POST'])
def run_parser():
    """Run parser for all platforms and send to Telegram"""
    try:
        # Run the script
        result = subprocess.run(
            ['python3', SCRIPT_PATH],
            capture_output=True,
            text=True,
            cwd=os.path.dirname(SCRIPT_PATH),
            timeout=300  # 5 minutes timeout
        )

        # Parse JSON from output
        output_lines = result.stdout.strip().split('\n')
        json_started = False
        json_lines = []

        for line in output_lines:
            if line.strip() == '{':
                json_started = True
            if json_started:
                json_lines.append(line)
            if json_started and line.strip() == '}':
                break

        if json_lines:
            result_data = json.loads('\n'.join(json_lines))
            return jsonify(result_data)
        else:
            return jsonify({
                'success': True,
                'message': 'Parser executed',
                'stdout': result.stdout,
                'stderr': result.stderr
            })

    except subprocess.TimeoutExpired:
        return jsonify({
            'success': False,
            'error': 'Parser execution timed out (>5 minutes)'
        }), 500
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/parse-async', methods=['POST'])
def run_parser_async():
    """Run parser asynchronously in background"""
    try:
        # Run in background
        process = subprocess.Popen(
            ['python3', SCRIPT_PATH],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=os.path.dirname(SCRIPT_PATH)
        )

        return jsonify({
            'success': True,
            'message': 'Parser started in background',
            'pid': process.pid
        })

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/get-unsent', methods=['GET'])
def get_unsent():
    """Get unsent listings from database"""
    try:
        sys.path.insert(0, os.path.dirname(SCRIPT_PATH))
        from database.models import init_db, get_unsent_listings

        limit = int(request.args.get('limit', 20))
        db = init_db('rental_parser.db')
        listings = get_unsent_listings(db, limit=limit)

        result = []
        for listing in listings:
            result.append({
                'id': listing.id,
                'platform': listing.platform,
                'listing_id': listing.listing_id,
                'url': listing.url,
                'title': listing.title,
                'price': listing.price,
                'address': listing.address,
                'rooms': listing.rooms,
                'area': listing.area,
                'phone': listing.phone,
                'image': f'https://via.placeholder.com/600x400/4A90E2/ffffff?text={listing.platform}+{listing.listing_id}',
                'created_at': listing.created_at.isoformat() if listing.created_at else None
            })

        db.close()
        return jsonify(result)

    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/status', methods=['GET'])
def status():
    """Get API status and configuration"""
    try:
        # Load .env to check configuration
        from dotenv import load_dotenv
        load_dotenv()

        telegram_configured = bool(os.getenv('TELEGRAM_BOT_TOKEN')) and bool(os.getenv('TELEGRAM_CHAT_IDS'))

        return jsonify({
            'status': 'running',
            'script_path': SCRIPT_PATH,
            'script_exists': os.path.exists(SCRIPT_PATH),
            'telegram_configured': telegram_configured,
            'city': os.getenv('CITY', 'москва'),
            'max_pages': os.getenv('MAX_PAGES', '5'),
            'auto_dial_enabled': os.getenv('AUTO_DIAL_ENABLED', 'true')
        })

    except Exception as e:
        return jsonify({
            'status': 'error',
            'error': str(e)
        }), 500


if __name__ == '__main__':
    print("=" * 60)
    print("Starting Rental Parser API...")
    print("=" * 60)
    print(f"API will be available at: http://localhost:5555")
    print(f"Script path: {SCRIPT_PATH}")
    print(f"Script exists: {os.path.exists(SCRIPT_PATH)}")
    print("")
    print("Endpoints:")
    print("  GET  /health        - Health check")
    print("  GET  /status        - API status and configuration")
    print("  GET  /get-unsent    - Get unsent listings from DB")
    print("  POST /parse         - Run parser (wait for completion)")
    print("  POST /parse-async   - Run parser (background)")
    print("=" * 60)
    print("")

    app.run(host='0.0.0.0', port=5555, debug=False)
