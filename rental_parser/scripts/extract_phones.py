#!/usr/bin/env python3
"""
Script to extract phone numbers from n8n
"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import RentalParserOrchestrator

def main():
    orchestrator = RentalParserOrchestrator(
        city='москва',
        db_path='rental_parser.db'
    )

    try:
        count = orchestrator.extract_phones(limit=10)
        print(f"SUCCESS: Extracted {count} phone numbers")
        return 0
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    finally:
        orchestrator.close()

if __name__ == '__main__':
    exit(main())
