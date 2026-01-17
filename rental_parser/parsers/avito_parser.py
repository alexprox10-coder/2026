"""
Parser for Avito.ru
"""
import json
import re
from typing import List, Dict, Optional
from urllib.parse import urlencode, urljoin
from bs4 import BeautifulSoup
from .base_parser import BaseParser
from ..utils.proxy_manager import RequestSession, ProxyManager, RateLimiter


class AvitoParser(BaseParser):
    """Parser for Avito.ru long-term apartment rentals"""

    BASE_URL = "https://www.avito.ru"
    SEARCH_URL = "https://www.avito.ru/moskva/kvartiry/sdam/na_dlitelnyy_srok"

    def __init__(self, city: str = "москва", request_session: Optional[RequestSession] = None):
        super().__init__(city)
        self.request_session = request_session or RequestSession(
            proxy_manager=ProxyManager(),
            rate_limiter=RateLimiter(min_delay=5.0, max_delay=8.0)  # Avito is strict
        )

        # City URL mapping
        self.city_urls = {
            'москва': '/moskva',
            'санкт-петербург': '/sankt-peterburg',
            'новосибирск': '/novosibirsk',
            'екатеринбург': '/ekaterinburg',
        }

    def parse(self, max_pages: int = 5) -> List[Dict]:
        """
        Parse long-term rental listings from Avito

        Args:
            max_pages: Maximum number of pages to parse

        Returns:
            List of parsed listings
        """
        listings = []
        page = 1

        while page <= max_pages:
            self.log_progress(f"Parsing Avito.ru page {page}/{max_pages}")

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

        city_path = self.city_urls.get(self.city.lower(), '/moskva')

        # Avito URL structure
        params = {
            'p': page,
        }

        url = f"{self.BASE_URL}{city_path}/kvartiry/sdam/na_dlitelnyy_srok"
        if page > 1:
            url += f"?{urlencode(params)}"

        try:
            response = self.request_session.get(url)
            soup = BeautifulSoup(response.text, 'html.parser')

            listings = []

            # Avito uses data-marker attributes
            cards = soup.find_all('div', attrs={'data-marker': 'item'})

            for card in cards:
                listing = self._parse_card(card)
                if listing and self.is_long_term_rental(listing.get('title', ''), listing.get('description', '')):
                    listings.append(listing)

            # Alternative: look for JSON-LD structured data
            if not listings:
                listings = self._parse_json_ld(soup)

            return listings

        except Exception as e:
            self.logger.error(f"Error in _parse_page: {e}")
            return []

    def _parse_card(self, card) -> Optional[Dict]:
        """Parse single listing card"""
        try:
            # Extract URL
            link = card.find('a', attrs={'data-marker': 'item-title'})
            if not link:
                return None

            href = link.get('href', '')
            url = urljoin(self.BASE_URL, href)

            # Extract listing ID from URL
            match = re.search(r'_(\d+)$', url)
            listing_id_num = match.group(1) if match else ''

            # Extract title
            title = link.get_text(strip=True)

            # Extract price
            price_elem = card.find('span', attrs={'data-marker': 'item-price'})
            price_text = price_elem.get_text(strip=True) if price_elem else ''
            price = self.clean_price(price_text)

            # Extract address/location
            address_elem = card.find('div', attrs={'data-marker': 'item-address'})
            address = address_elem.get_text(strip=True) if address_elem else ''

            # Extract description
            desc_elem = card.find('div', attrs={'data-marker': 'item-description'})
            description = desc_elem.get_text(strip=True) if desc_elem else ''

            # Extract rooms and area
            rooms = self.extract_rooms(title)
            area = self.extract_area(title + ' ' + description)

            return {
                'platform': 'avito',
                'listing_id': self.generate_listing_id('avito', url),
                'url': url,
                'phone': None,  # Requires clicking "Show phone" button
                'title': title,
                'address': address,
                'price': price,
                'rooms': rooms,
                'area': area,
                'floor': None,
                'total_floors': None,
                'description': description,
                'raw_data': ''
            }

        except Exception as e:
            self.logger.error(f"Error parsing card: {e}")
            return None

    def _parse_json_ld(self, soup: BeautifulSoup) -> List[Dict]:
        """Parse JSON-LD structured data"""
        listings = []

        scripts = soup.find_all('script', type='application/ld+json')
        for script in scripts:
            try:
                data = json.loads(script.string)

                # Handle both single item and list
                items = data if isinstance(data, list) else [data]

                for item in items:
                    if item.get('@type') in ['Product', 'RealEstateListing']:
                        listing = self._parse_json_ld_item(item)
                        if listing:
                            listings.append(listing)

            except (json.JSONDecodeError, TypeError):
                continue

        return listings

    def _parse_json_ld_item(self, item: Dict) -> Optional[Dict]:
        """Parse single JSON-LD item"""
        try:
            url = item.get('url', '')
            if not url:
                return None

            title = item.get('name', '')
            description = item.get('description', '')

            # Price
            offers = item.get('offers', {})
            price_text = offers.get('price', '')
            price = self.clean_price(str(price_text))

            # Address
            address_obj = item.get('address', {})
            address = address_obj.get('streetAddress', '') if isinstance(address_obj, dict) else ''

            rooms = self.extract_rooms(title)
            area = self.extract_area(title + ' ' + description)

            return {
                'platform': 'avito',
                'listing_id': self.generate_listing_id('avito', url),
                'url': url,
                'phone': None,
                'title': title,
                'address': address,
                'price': price,
                'rooms': rooms,
                'area': area,
                'floor': None,
                'total_floors': None,
                'description': description,
                'raw_data': json.dumps(item, ensure_ascii=False)
            }

        except Exception as e:
            self.logger.error(f"Error parsing JSON-LD item: {e}")
            return None

    def extract_phone(self, listing_url: str) -> Optional[str]:
        """
        Extract phone number from listing page

        Note: Avito heavily protects phone numbers. They require:
        - Clicking "Show phone" button
        - Solving CAPTCHA
        - Being logged in

        This is a basic implementation that may not work.

        Args:
            listing_url: URL of the listing

        Returns:
            Phone number or None
        """
        try:
            response = self.request_session.get(listing_url)
            soup = BeautifulSoup(response.text, 'html.parser')

            # Try to find phone in page source (usually hidden)
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

            # Try to find phone button data attributes
            phone_button = soup.find('a', attrs={'data-marker': 'item-contact-bar/call'})
            if phone_button:
                phone_href = phone_button.get('href', '')
                if 'tel:' in phone_href:
                    phone = phone_href.replace('tel:', '').strip()
                    return self.clean_phone(phone)

            # Look for JSON data containing phone
            scripts = soup.find_all('script')
            for script in scripts:
                if script.string and 'phone' in script.string.lower():
                    for pattern in phone_patterns:
                        match = re.search(pattern, script.string)
                        if match:
                            return self.clean_phone(match.group(0))

            return None

        except Exception as e:
            self.logger.error(f"Error extracting phone from {listing_url}: {e}")
            return None

    def get_phone_via_api(self, item_id: str) -> Optional[str]:
        """
        Attempt to get phone via Avito API (requires authentication)

        This is a placeholder - actual implementation would require:
        - Avito account
        - Session cookies
        - CSRF tokens
        - Possibly solving CAPTCHA

        Args:
            item_id: Avito item ID

        Returns:
            Phone number or None
        """
        # Placeholder for API implementation
        self.logger.warning("Avito phone extraction via API not implemented - requires authentication")
        return None
