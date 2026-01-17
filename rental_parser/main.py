"""
Main orchestrator for rental property parser
"""
import argparse
import logging
import sys
from datetime import datetime
from typing import List, Dict

from database.models import init_db, RentalListing, ParsingSession
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

logger = logging.getLogger('RentalParser')


class RentalParserOrchestrator:
    """Main orchestrator for all parsers"""

    def __init__(self, city: str = "москва", db_path: str = "rental_parser.db", proxy_list: List[str] = None):
        """
        Initialize orchestrator

        Args:
            city: City name for searching
            db_path: Path to SQLite database
            proxy_list: List of proxy URLs
        """
        self.city = city
        self.db_session = init_db(db_path)

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
            session_record = ParsingSession(platform=platform_name)
            self.db_session.add(session_record)
            self.db_session.commit()

            try:
                parser = self.parsers[platform_name]
                listings = parser.parse(max_pages=max_pages)

                # Save to database
                new_count = self._save_listings(listings, platform_name)

                # Update session
                session_record.listings_found = len(listings)
                session_record.listings_new = new_count
                session_record.completed_at = datetime.utcnow()
                session_record.status = 'completed'
                self.db_session.commit()

                stats[platform_name] = {
                    'found': len(listings),
                    'new': new_count
                }

                logger.info(f"✓ {platform_name.upper()}: Found {len(listings)} listings, {new_count} new")

            except Exception as e:
                logger.error(f"✗ Error parsing {platform_name}: {e}", exc_info=True)

                session_record.status = 'failed'
                session_record.error_message = str(e)
                session_record.completed_at = datetime.utcnow()
                self.db_session.commit()

                stats[platform_name] = {
                    'found': 0,
                    'new': 0,
                    'error': str(e)
                }

        return stats

    def _save_listings(self, listings: List[Dict], platform: str) -> int:
        """
        Save listings to database

        Args:
            listings: List of parsed listings
            platform: Platform name

        Returns:
            Number of new listings added
        """
        new_count = 0

        for listing_data in listings:
            # Check if listing already exists
            existing = self.db_session.query(RentalListing).filter(
                RentalListing.listing_id == listing_data['listing_id']
            ).first()

            if existing:
                # Update last_seen
                existing.last_seen = datetime.utcnow()
                logger.debug(f"Updated existing listing: {listing_data['listing_id']}")
            else:
                # Create new listing
                listing = RentalListing(**listing_data)
                self.db_session.add(listing)
                new_count += 1
                logger.debug(f"Added new listing: {listing_data['listing_id']}")

        self.db_session.commit()
        return new_count

    def extract_phones(self, limit: int = 10) -> int:
        """
        Extract phone numbers for listings without phones

        Args:
            limit: Maximum number of listings to process

        Returns:
            Number of phones extracted
        """
        # Get listings without phones
        listings = self.db_session.query(RentalListing).filter(
            RentalListing.phone.is_(None),
            RentalListing.is_active == True
        ).limit(limit).all()

        extracted_count = 0

        for listing in listings:
            parser = self.parsers.get(listing.platform)
            if not parser:
                continue

            try:
                logger.info(f"Extracting phone for {listing.platform}:{listing.listing_id}")
                phone = parser.extract_phone(listing.url)

                if phone:
                    listing.phone = phone
                    extracted_count += 1
                    logger.info(f"✓ Extracted phone: {phone}")
                else:
                    logger.warning(f"✗ Could not extract phone from {listing.url}")

            except Exception as e:
                logger.error(f"Error extracting phone: {e}")

        self.db_session.commit()
        return extracted_count

    def get_stats(self) -> Dict:
        """Get database statistics"""
        total = self.db_session.query(RentalListing).count()
        unsent = self.db_session.query(RentalListing).filter(
            RentalListing.sent_to_manager == False
        ).count()

        by_platform = {}
        for platform in ['cian', 'yandex', 'avito']:
            count = self.db_session.query(RentalListing).filter(
                RentalListing.platform == platform
            ).count()
            by_platform[platform] = count

        return {
            'total': total,
            'unsent': unsent,
            'by_platform': by_platform
        }

    def close(self):
        """Close database connection"""
        self.db_session.close()
        self.request_session.close()


def main():
    """CLI entry point"""
    parser = argparse.ArgumentParser(description='Rental Property Parser')
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
    parser.add_argument('--db-path', default='rental_parser.db',
                        help='Database path')
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
    orchestrator = RentalParserOrchestrator(
        city=args.city,
        db_path=args.db_path,
        proxy_list=proxy_list
    )

    try:
        if args.stats:
            # Show statistics
            stats = orchestrator.get_stats()
            print("\n" + "=" * 60)
            print("DATABASE STATISTICS")
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
