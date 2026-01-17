"""
Parser for Cian.ru
"""
import json
import re
from typing import List, Dict, Optional
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from ..utils.proxy_manager import RequestSession, ProxyManager, RateLimiter


class CianParser(BaseParser):
    """Parser for Cian.ru long-term apartment rentals"""

    BASE_URL = "https://www.cian.ru"
    API_URL = "https://api.cian.ru/search-offers/v2/search-offers-desktop/"

    def __init__(self, city: str = "москва", request_session: Optional[RequestSession] = None):
        super().__init__(city)
        self.request_session = request_session or RequestSession(
            proxy_manager=ProxyManager(),
            rate_limiter=RateLimiter(min_delay=3.0, max_delay=6.0)
        )

    def parse(self, max_pages: int = 5) -> List[Dict]:
        """
        Parse long-term rental listings from Cian

        Args:
            max_pages: Maximum number of pages to parse

        Returns:
            List of parsed listings
        """
        listings = []
        page = 1

        while page <= max_pages:
            self.log_progress(f"Parsing Cian.ru page {page}/{max_pages}")

            try:
                page_listings = self._parse_page(page)

                if not page_listings:
                    self.log_progress(f"No more listings found on page {page}")
                    break

                listings.extend(page_listings)
                self.log_progress(f"Found {len(page_listings)} listings on page {page}")

                page += 1

            except Exception as e:
                self.logger.error(f"Error parsing page {page}: {e}")
                break

        self.log_progress(f"Total listings found: {len(listings)}")
        return listings

    def _parse_page(self, page: int) -> List[Dict]:
        """Parse single page of listings"""

        # Cian API payload for long-term rentals
        payload = {
            "jsonQuery": {
                "region": {"type": "terms", "value": [1]},  # Moscow region ID
                "_type": "flatrent",  # Apartment rental
                "room": {"type": "terms", "value": [1, 2, 3, 4, 5, 6, 9]},  # Room counts
                "engine_version": {"type": "term", "value": 2},
                "page": {"type": "term", "value": page},
                "for_day": {"type": "term", "value": "!1"}  # Exclude daily rentals
            }
        }

        headers = {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
        }

        try:
            response = self.request_session.get(
                self.API_URL,
                headers=headers,
                json=payload
            )

            data = response.json()
            offers = data.get('data', {}).get('offersSerialized', [])

            listings = []
            for offer in offers:
                listing = self._parse_offer(offer)
                if listing and self.is_long_term_rental(listing.get('title', ''), listing.get('description', '')):
                    listings.append(listing)

            return listings

        except Exception as e:
            self.logger.error(f"Error in _parse_page: {e}")
            return []

    def _parse_offer(self, offer: Dict) -> Optional[Dict]:
        """Parse single offer from API response"""

        try:
            # Extract data from JSON
            listing_id = str(offer.get('id'))
            url = offer.get('fullUrl', f"{self.BASE_URL}/rent/flat/{listing_id}/")

            # Basic info
            title = offer.get('title', '')
            description = offer.get('description', '')
            price = offer.get('bargainTerms', {}).get('price')

            # Location
            geo = offer.get('geo', {})
            address_parts = []

            if geo.get('userInput'):
                address_parts.append(geo['userInput'])

            address = ', '.join(filter(None, address_parts))

            # Property details
            total_area = offer.get('totalArea')
            rooms_count = offer.get('roomsCount')
            floor = offer.get('floorNumber')
            total_floors = offer.get('building', {}).get('floorsCount')

            # Try to extract phone (might not be in API response)
            phones = offer.get('phones', [])
            phone = None
            if phones:
                phone = self.clean_phone(phones[0].get('number', ''))

            return {
                'platform': 'cian',
                'listing_id': self.generate_listing_id('cian', url),
                'url': url,
                'phone': phone,
                'title': title,
                'address': address,
                'price': float(price) if price else None,
                'rooms': rooms_count,
                'area': total_area,
                'floor': floor,
                'total_floors': total_floors,
                'description': description,
                'raw_data': json.dumps(offer, ensure_ascii=False)
            }

        except Exception as e:
            self.logger.error(f"Error parsing offer: {e}")
            return None

    def extract_phone(self, listing_url: str) -> Optional[str]:
        """
        Extract phone number from listing page

        Args:
            listing_url: URL of the listing

        Returns:
            Phone number or None
        """
        try:
            response = self.request_session.get(listing_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Cian often hides phones behind a "Show phone" button
            # Look for phone in various places
            phone_patterns = [
                r'\+7\s?\(\d{3}\)\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}',
                r'8\s?\(\d{3}\)\s?\d{3}[-\s]?\d{2}[-\s]?\d{2}',
                r'\+7\d{10}',
                r'8\d{10}'
            ]

            page_text = soup.get_text()

            for pattern in phone_patterns:
                match = re.search(pattern, page_text)
                if match:
                    return self.clean_phone(match.group(0))

            # Try to find in data attributes
            phone_elements = soup.find_all(attrs={'data-phone': True})
            if phone_elements:
                return self.clean_phone(phone_elements[0].get('data-phone'))

            # Look for phone button and extract from onclick/data attributes
            phone_button = soup.find('button', attrs={'data-name': 'PhoneButton'})
            if phone_button:
                onclick = phone_button.get('onclick', '')
                phone_match = re.search(r'\+?\d[\d\s\(\)\-]{9,}', onclick)
                if phone_match:
                    return self.clean_phone(phone_match.group(0))

            return None

        except Exception as e:
            self.logger.error(f"Error extracting phone from {listing_url}: {e}")
            return None

    def get_search_url(self) -> str:
        """Get human-readable search URL"""
        return f"{self.BASE_URL}/cat.php?deal_type=rent&engine_version=2&offer_type=flat&region=1"
