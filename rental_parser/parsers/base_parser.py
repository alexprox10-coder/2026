"""
Base parser class for all platforms
"""
import re
import logging
from abc import ABC, abstractmethod
from typing import List, Dict, Optional
from datetime import datetime
import hashlib


class BaseParser(ABC):
    """Base class for all property parsers"""

    def __init__(self, city: str = "москва"):
        """
        Initialize parser

        Args:
            city: City name for searching
        """
        self.city = city
        self.logger = logging.getLogger(self.__class__.__name__)

    @abstractmethod
    def parse(self, max_pages: int = 5) -> List[Dict]:
        """
        Parse listings from platform

        Args:
            max_pages: Maximum number of pages to parse

        Returns:
            List of parsed listings
        """
        pass

    @abstractmethod
    def extract_phone(self, listing_url: str) -> Optional[str]:
        """
        Extract phone number from listing page

        Args:
            listing_url: URL of the listing

        Returns:
            Phone number or None
        """
        pass

    def generate_listing_id(self, platform: str, url: str) -> str:
        """
        Generate unique listing ID

        Args:
            platform: Platform name
            url: Listing URL

        Returns:
            Unique ID
        """
        # Extract ID from URL or use hash
        url_hash = hashlib.md5(url.encode()).hexdigest()[:16]
        return f"{platform}_{url_hash}"

    def clean_phone(self, phone: str) -> Optional[str]:
        """
        Clean and format phone number

        Args:
            phone: Raw phone number

        Returns:
            Cleaned phone number or None
        """
        if not phone:
            return None

        # Remove all non-digit characters
        digits = re.sub(r'\D', '', phone)

        # Russian phone numbers: +7XXXXXXXXXX or 8XXXXXXXXXX
        if len(digits) == 11 and digits[0] in ['7', '8']:
            return f"+7{digits[1:]}"
        elif len(digits) == 10:
            return f"+7{digits}"

        return phone if digits else None

    def clean_price(self, price_str: str) -> Optional[float]:
        """
        Extract price from string

        Args:
            price_str: Price string

        Returns:
            Price as float or None
        """
        if not price_str:
            return None

        # Remove all non-digit characters except decimal point
        price_clean = re.sub(r'[^\d.]', '', price_str)

        try:
            return float(price_clean)
        except (ValueError, TypeError):
            return None

    def is_long_term_rental(self, title: str, description: str = "") -> bool:
        """
        Check if listing is for long-term rental (not daily)

        Args:
            title: Listing title
            description: Listing description

        Returns:
            True if long-term rental
        """
        text = f"{title} {description}".lower()

        # Keywords indicating daily rental
        daily_keywords = [
            'посуточно', 'сутки', 'hourly', 'почасовая',
            'час', 'на день', 'на сутки', 'краткосрочно'
        ]

        # Keywords indicating sale
        sale_keywords = [
            'продам', 'продажа', 'купить', 'продается',
            'sale', 'buy', 'selling'
        ]

        for keyword in daily_keywords + sale_keywords:
            if keyword in text:
                return False

        return True

    def extract_rooms(self, title: str) -> Optional[int]:
        """
        Extract number of rooms from title

        Args:
            title: Listing title

        Returns:
            Number of rooms or None
        """
        # Look for patterns like "1-комн", "2-к", "3 комнаты"
        patterns = [
            r'(\d+)[-\s]*комн',
            r'(\d+)[-\s]*к[.\s]',
            r'(\d+)[-\s]*room',
            r'студия'
        ]

        title_lower = title.lower()

        if 'студия' in title_lower:
            return 0  # Studio apartment

        for pattern in patterns:
            match = re.search(pattern, title_lower)
            if match:
                if 'студия' in match.group(0):
                    return 0
                try:
                    return int(match.group(1))
                except (ValueError, IndexError):
                    continue

        return None

    def extract_area(self, text: str) -> Optional[float]:
        """
        Extract area in square meters

        Args:
            text: Text containing area

        Returns:
            Area in m² or None
        """
        # Look for patterns like "50 м²", "75.5м2", "80 кв.м"
        patterns = [
            r'(\d+(?:\.\d+)?)\s*м[²2]',
            r'(\d+(?:\.\d+)?)\s*кв\.?\s*м',
            r'(\d+(?:\.\d+)?)\s*sq\.?\s*m'
        ]

        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                try:
                    return float(match.group(1))
                except (ValueError, IndexError):
                    continue

        return None

    def log_progress(self, message: str):
        """Log progress message"""
        self.logger.info(f"[{datetime.now().strftime('%H:%M:%S')}] {message}")
