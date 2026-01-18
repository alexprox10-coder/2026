#!/usr/bin/env python3
"""
Script to run parser from n8n with Firebase
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main_firebase import RentalParserOrchestratorFirebase

def main():
    credentials_path = os.getenv('FIREBASE_CREDENTIALS_PATH', 'firebase-credentials.json')

    orchestrator = RentalParserOrchestratorFirebase(
        city='москва',
        credentials_path=credentials_path
    )

    try:
        stats = orchestrator.parse_all(max_pages=5)
        total_found = sum(s.get('found', 0) for s in stats.values())
        total_new = sum(s.get('new', 0) for s in stats.values())

        print(f"SUCCESS: Found {total_found} listings, {total_new} new")
        return 0
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    finally:
        orchestrator.close()

if __name__ == '__main__':
    exit(main())
