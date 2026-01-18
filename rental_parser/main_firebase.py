"""
Main orchestrator for rental property parser with Firebase
"""
import argparse
import logging
import sys
from datetime import datetime
from typing import List, Dict

from database.firebase_config import init_firebase
from database.firebase_models import (
    RentalListingFirebase,
    ParsingSessionFirebase
)
from parsers import CianParser, YandexRealtyParser, AvitoParser
from utils.proxy_manager import ProxyManager, RateLimiter, RequestSession


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logs/parser.log'),
        logging.StreamHandler(sys.stdout)
    ]
)

logger = logging.getLogger('RentalParserFirebase')


class RentalParserOrchestratorFirebase:
    """Main orchestrator for all parsers with Firebase backend"""

    def __init__(self, city: str = "москва", proxy_list: List[str] = None, credentials_path: str = None):
        """
        Initialize orchestrator

        Args:
            city: City name for searching
            proxy_list: List of proxy URLs
            credentials_path: Path to Firebase credentials JSON
        """
        self.city = city

        # Initialize Firebase
        try:
            init_firebase(credentials_path)
            logger.info("✓ Firebase initialized successfully")
        except Exception as e:
            logger.error(f"✗ Failed to initialize Firebase: {e}")
            raise

        # Setup request session with proxies
        proxy_manager = ProxyManager(proxy_list or [])
        rate_limiter = RateLimiter(min_delay=2.0, max_delay=5.0)
        self.request_session = RequestSession(proxy_manager, rate_limiter)

        # Initialize parsers
        self.parsers = {
            'cian': CianParser(city, self.request_session),
            'yandex': YandexRealtyParser(city, self.request_session),
            'avito': AvitoParser(city, self.request_session),
        }

    def parse_all(self, max_pages: int = 5, platforms: List[str] = None) -> Dict[str, int]:
        """
        Run all parsers

        Args:
            max_pages: Maximum pages to parse per platform
            platforms: List of platforms to parse (None = all)

        Returns:
            Dictionary with statistics per platform
        """
        if platforms is None:
            platforms = list(self.parsers.keys())

        stats = {}

        for platform_name in platforms:
            if platform_name not in self.parsers:
                logger.warning(f"Unknown platform: {platform_name}")
                continue

            logger.info(f"=" * 60)
            logger.info(f"Starting parser for {platform_name.upper()}")
            logger.info(f"=" * 60)

            # Create parsing session
            session_id = ParsingSessionFirebase.create(platform=platform_name)

            try:
                parser = self.parsers[platform_name]
                listings = parser.parse(max_pages=max_pages)

                # Save to Firebase
                new_count = self._save_listings(listings, platform_name)

                # Update session
                ParsingSessionFirebase.complete(
                    session_id,
                    listings_found=len(listings),
                    listings_new=new_count
                )

                stats[platform_name] = {
                    'found': len(listings),
                    'new': new_count
                }

                logger.info(f"✓ {platform_name.upper()}: Found {len(listings)} listings, {new_count} new")

            except Exception as e:
                logger.error(f"✗ Error parsing {platform_name}: {e}", exc_info=True)

                ParsingSessionFirebase.fail(session_id, str(e))

                stats[platform_name] = {
                    'found': 0,
                    'new': 0,
                    'error': str(e)
                }

        return stats

    def _save_listings(self, listings: List[Dict], platform: str) -> int:
        """
        Save listings to Firebase

        Args:
            listings: List of parsed listings
            platform: Platform name

        Returns:
            Number of new listings added
        """
        new_count = 0

        for listing_data in listings:
            try:
                # Check if listing already exists
                if RentalListingFirebase.exists(listing_data['listing_id']):
                    # Update last_seen
                    RentalListingFirebase.update_last_seen(listing_data['listing_id'])
                    logger.debug(f"Updated existing listing: {listing_data['listing_id']}")
                else:
                    # Create new listing
                    RentalListingFirebase.create(listing_data)
                    new_count += 1
                    logger.debug(f"Added new listing: {listing_data['listing_id']}")

            except Exception as e:
                logger.error(f"Error saving listing {listing_data.get('listing_id')}: {e}")

        return new_count

    def extract_phones(self, limit: int = 10) -> int:
        """
        Extract phone numbers for listings without phones

        Args:
            limit: Maximum number of listings to process

        Returns:
            Number of phones extracted
        """
        # Get unsent listings without phones
        unsent = RentalListingFirebase.get_unsent(limit=limit * 3)  # Get more to filter
        without_phones = [l for l in unsent if not l.get('phone')][:limit]

        extracted_count = 0

        for listing in without_phones:
            parser = self.parsers.get(listing['platform'])
            if not parser:
                continue

            try:
                logger.info(f"Extracting phone for {listing['platform']}:{listing['listing_id']}")
                phone = parser.extract_phone(listing['url'])

                if phone:
                    # Update listing with phone
                    from .firebase_config import get_db
                    db = get_db()
                    doc_ref = db.collection(RentalListingFirebase.COLLECTION).document(listing['listing_id'])
                    doc_ref.update({'phone': phone})

                    extracted_count += 1
                    logger.info(f"✓ Extracted phone: {phone}")
                else:
                    logger.warning(f"✗ Could not extract phone from {listing['url']}")

            except Exception as e:
                logger.error(f"Error extracting phone: {e}")

        return extracted_count

    def get_stats(self) -> Dict:
        """Get database statistics"""
        return RentalListingFirebase.get_stats()

    def close(self):
        """Close connections"""
        self.request_session.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Rental Property Parser with Firebase')
    parser.add_argument('--city', default='москва', help='City name')
    parser.add_argument('--max-pages', type=int, default=5, help='Max pages per platform')
    parser.add_argument('--platforms', nargs='+', choices=['cian', 'yandex', 'avito'],
                        help='Platforms to parse (default: all)')
    parser.add_argument('--extract-phones', action='store_true',
                        help='Extract phone numbers for listings')
    parser.add_argument('--phone-limit', type=int, default=10,
                        help='Max listings to extract phones for')
    parser.add_argument('--stats', action='store_true',
                        help='Show database statistics')
    parser.add_argument('--firebase-creds', help='Path to Firebase credentials JSON')
    parser.add_argument('--proxy-file', help='File with proxy list (one per line)')

    args = parser.parse_args()

    # Load proxies if provided
    proxy_list = []
    if args.proxy_file:
        try:
            with open(args.proxy_file, 'r') as f:
                proxy_list = [line.strip() for line in f if line.strip()]
            logger.info(f"Loaded {len(proxy_list)} proxies from {args.proxy_file}")
        except Exception as e:
            logger.error(f"Error loading proxies: {e}")

    # Initialize orchestrator
    orchestrator = RentalParserOrchestratorFirebase(
        city=args.city,
        proxy_list=proxy_list,
        credentials_path=args.firebase_creds
    )

    try:
        if args.stats:
            # Show statistics
            stats = orchestrator.get_stats()
            print("\n" + "=" * 60)
            print("FIREBASE DATABASE STATISTICS")
            print("=" * 60)
            print(f"Total listings: {stats['total']}")
            print(f"Unsent listings: {stats['unsent']}")
            print("\nBy platform:")
            for platform, count in stats['by_platform'].items():
                print(f"  {platform.capitalize()}: {count}")
            print("=" * 60 + "\n")

        elif args.extract_phones:
            # Extract phone numbers
            logger.info(f"Extracting phones for up to {args.phone_limit} listings...")
            count = orchestrator.extract_phones(limit=args.phone_limit)
            logger.info(f"✓ Extracted {count} phone numbers")

        else:
            # Run parsers
            logger.info(f"Starting rental property parser for {args.city}")
            logger.info(f"Max pages: {args.max_pages}")

            stats = orchestrator.parse_all(
                max_pages=args.max_pages,
                platforms=args.platforms
            )

            # Print summary
            print("\n" + "=" * 60)
            print("PARSING SUMMARY")
            print("=" * 60)
            for platform, platform_stats in stats.items():
                if 'error' in platform_stats:
                    print(f"{platform.upper()}: ERROR - {platform_stats['error']}")
                else:
                    print(f"{platform.upper()}: {platform_stats['found']} found, {platform_stats['new']} new")
            print("=" * 60 + "\n")

    finally:
        orchestrator.close()


if __name__ == '__main__':
    main()
