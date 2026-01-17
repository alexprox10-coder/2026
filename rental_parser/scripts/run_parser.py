#!/usr/bin/env python3
"""
Script to run parser from n8n
"""
import sys
import os

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from main import RentalParserOrchestrator

def main():
    orchestrator = RentalParserOrchestrator(
        city='москва',
        db_path='rental_parser.db'
    )

    try:
        stats = orchestrator.parse_all(max_pages=5)
        print(f"SUCCESS: Parsed {sum(s['found'] for s in stats.values())} listings")
        return 0
    except Exception as e:
        print(f"ERROR: {str(e)}", file=sys.stderr)
        return 1
    finally:
        orchestrator.close()

if __name__ == '__main__':
    exit(main())
