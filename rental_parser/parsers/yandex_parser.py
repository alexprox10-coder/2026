"""
Parser for Yandex.Realty
"""
import json
import re
from typing import List, Dict, Optional
from urllib.parse import urlencode
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from ..utils.proxy_manager import RequestSession, ProxyManager, RateLimiter


class YandexRealtyParser(BaseParser):
    """Parser for Yandex.Realty long-term apartment rentals"""

    BASE_URL = "https://realty.yandex.ru"
    SEARCH_URL = "https://realty.yandex.ru/moskva/snyat/kvartira/"

    def __init__(self, city: str = "москва", request_session: Optional[RequestSession] = None):
        super().__init__(city)
        self.request_session = request_session or RequestSession(
            proxy_manager=ProxyManager(),
            rate_limiter=RateLimiter(min_delay=4.0, max_delay=7.0)
        )

    def parse(self, max_pages: int = 5) -> List[Dict]:
        """
        Parse long-term rental listings from Yandex.Realty

        Args:
            max_pages: Maximum number of pages to parse

        Returns:
            List of parsed listings
        """
        listings = []
        page = 1

        while page <= max_pages:
            self.log_progress(f"Parsing Yandex.Realty page {page}/{max_pages}")

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

        params = {
            'page': page,
            'type': 'rent',
            'category': 'flat',
            'rentTime': 'large',  # Long-term rental (not daily)
        }

        url = f"{self.SEARCH_URL}?{urlencode(params)}"

        try:
            response = self.request_session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Yandex.Realty uses React, data is often in script tags
            listings = []

            # Try to find JSON data in script tags
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)
                    offers = self._extract_offers_from_json(data)
                    listings.extend(offers)
                except (json.JSONDecodeError, TypeError):
                    continue

            # Fallback: parse HTML cards
            if not listings:
                listings = self._parse_html_cards(soup)

            return listings

        except Exception as e:
            self.logger.error(f"Error in _parse_page: {e}")
            return []

    def _extract_offers_from_json(self, data: Dict) -> List[Dict]:
        """Extract offers from JSON data in page"""
        offers = []

        # Navigate JSON structure (Yandex structure may vary)
        def find_offers(obj):
            if isinstance(obj, dict):
                # Look for offer-like structures
                if 'offerId' in obj or 'id' in obj:
                    parsed = self._parse_json_offer(obj)
                    if parsed:
                        offers.append(parsed)

                for value in obj.values():
                    find_offers(value)

            elif isinstance(obj, list):
                for item in obj:
                    find_offers(item)

        find_offers(data)
        return offers

    def _parse_json_offer(self, offer: Dict) -> Optional[Dict]:
        """Parse offer from JSON structure"""
        try:
            offer_id = str(offer.get('offerId') or offer.get('id'))
            if not offer_id:
                return None

            url = f"{self.BASE_URL}/offer/{offer_id}/"

            # Extract fields (structure may vary)
            title = offer.get('title') or offer.get('description', '')
            price = offer.get('price', {}).get('value') or offer.get('priceInfo', {}).get('price')

            # Location
            location = offer.get('location', {})
            address_parts = []

            if location.get('address'):
                address_parts.append(location['address'])
            elif location.get('fullName'):
                address_parts.append(location['fullName'])

            address = ', '.join(filter(None, address_parts))

            # Property details
            area = offer.get('area', {}).get('value') or offer.get('totalArea')
            rooms = offer.get('roomsTotal') or offer.get('rooms')
            floor = offer.get('floorsOffered', [None])[0] if 'floorsOffered' in offer else offer.get('floor')
            total_floors = offer.get('floorsTotal')

            description = offer.get('description', '')

            # Phone - usually not in initial JSON, needs separate request
            phone = None

            return {
                'platform': 'yandex',
                'listing_id': self.generate_listing_id('yandex', url),
                'url': url,
                'phone': phone,
                'title': title,
                'address': address,
                'price': float(price) if price else None,
                'rooms': rooms,
                'area': area,
                'floor': floor,
                'total_floors': total_floors,
                'description': description,
                'raw_data': json.dumps(offer, ensure_ascii=False)
            }

        except Exception as e:
            self.logger.error(f"Error parsing JSON offer: {e}")
            return None

    def _parse_html_cards(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse HTML cards as fallback"""
        listings = []

        # Find offer cards (class names may change)
        cards = soup.find_all('div', class_=re.compile(r'OfferCard'))

        for card in cards:
            try:
                # Extract URL
                link = card.find('a', class_=re.compile(r'link'))
                if not link:
                    continue

                href = link.get('href', '')
                if not href.startswith('http'):
                    href = self.BASE_URL + href

                # Extract title
                title_elem = card.find('h3') or card.find('a', class_=re.compile(r'title'))
                title = title_elem.get_text(strip=True) if title_elem else ''

                # Extract price
                price_elem = card.find('span', class_=re.compile(r'price'))
                price_text = price_elem.get_text(strip=True) if price_elem else ''
                price = self.clean_price(price_text)

                # Extract address
                address_elem = card.find('div', class_=re.compile(r'address'))
                address = address_elem.get_text(strip=True) if address_elem else ''

                # Extract rooms and area from title
                rooms = self.extract_rooms(title)
                area = self.extract_area(title)

                listing = {
                    'platform': 'yandex',
                    'listing_id': self.generate_listing_id('yandex', href),
                    'url': href,
                    'phone': None,
                    'title': title,
                    'address': address,
                    'price': price,
                    'rooms': rooms,
                    'area': area,
                    'floor': None,
                    'total_floors': None,
                    'description': '',
                    'raw_data': ''
                }

                if self.is_long_term_rental(title):
                    listings.append(listing)

            except Exception as e:
                self.logger.error(f"Error parsing HTML card: {e}")
                continue

        return listings

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

            # Look for phone in page text
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

            # Try to find in JSON data
            scripts = soup.find_all('script', type='application/json')
            for script in scripts:
                try:
                    data = json.loads(script.string)

                    def find_phone(obj):
                        if isinstance(obj, dict):
                            if 'phone' in obj:
                                return obj['phone']
                            if 'phoneNumber' in obj:
                                return obj['phoneNumber']
                            if 'phones' in obj and isinstance(obj['phones'], list) and obj['phones']:
                                return obj['phones'][0]

                            for value in obj.values():
                                result = find_phone(value)
                                if result:
                                    return result

                        elif isinstance(obj, list):
                            for item in obj:
                                result = find_phone(item)
                                if result:
                                    return result
                        return None

                    phone = find_phone(data)
                    if phone:
                        return self.clean_phone(phone)

                except (json.JSONDecodeError, TypeError):
                    continue

            return None

        except Exception as e:
            self.logger.error(f"Error extracting phone from {listing_url}: {e}")
            return None
