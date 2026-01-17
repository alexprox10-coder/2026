"""
Proxy rotation and anti-ban utilities
"""
import random
import time
from typing import List, Dict, Optional
import requests


class ProxyManager:
    """Manages proxy rotation to avoid bans"""

    def __init__(self, proxy_list: Optional[List[str]] = None):
        """
        Initialize proxy manager

        Args:
            proxy_list: List of proxy URLs in format: http://user:pass@host:port
        """
        self.proxy_list = proxy_list or []
        self.current_index = 0
        self.failed_proxies = set()

    def get_random_proxy(self) -> Optional[Dict[str, str]]:
        """Get random working proxy"""
        if not self.proxy_list:
            return None

        available_proxies = [p for p in self.proxy_list if p not in self.failed_proxies]

        if not available_proxies:
            # Reset failed proxies if all failed
            self.failed_proxies.clear()
            available_proxies = self.proxy_list

        proxy_url = random.choice(available_proxies)
        return {
            'http': proxy_url,
            'https': proxy_url
        }

    def mark_proxy_failed(self, proxy_dict: Dict[str, str]):
        """Mark proxy as failed"""
        if proxy_dict:
            self.failed_proxies.add(proxy_dict.get('http'))

    def get_next_proxy(self) -> Optional[Dict[str, str]]:
        """Get next proxy in rotation"""
        if not self.proxy_list:
            return None

        proxy_url = self.proxy_list[self.current_index]
        self.current_index = (self.current_index + 1) % len(self.proxy_list)

        return {
            'http': proxy_url,
            'https': proxy_url
        }


class UserAgentRotator:
    """Rotates user agents to mimic different browsers"""

    USER_AGENTS = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:121.0) Gecko/20100101 Firefox/121.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
        'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36 Edg/120.0.0.0',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36',
    ]

    @staticmethod
    def get_random() -> str:
        """Get random user agent"""
        return random.choice(UserAgentRotator.USER_AGENTS)


class RateLimiter:
    """Rate limiter to avoid being detected as a bot"""

    def __init__(self, min_delay: float = 2.0, max_delay: float = 5.0):
        """
        Initialize rate limiter

        Args:
            min_delay: Minimum delay in seconds
            max_delay: Maximum delay in seconds
        """
        self.min_delay = min_delay
        self.max_delay = max_delay
        self.last_request_time = 0

    def wait(self):
        """Wait before next request"""
        current_time = time.time()
        elapsed = current_time - self.last_request_time

        delay = random.uniform(self.min_delay, self.max_delay)

        if elapsed < delay:
            time.sleep(delay - elapsed)

        self.last_request_time = time.time()

    def set_delays(self, min_delay: float, max_delay: float):
        """Update delay settings"""
        self.min_delay = min_delay
        self.max_delay = max_delay


class RequestSession:
    """Safe request session with proxy rotation and rate limiting"""

    def __init__(
        self,
        proxy_manager: Optional[ProxyManager] = None,
        rate_limiter: Optional[RateLimiter] = None,
        timeout: int = 30
    ):
        self.proxy_manager = proxy_manager or ProxyManager()
        self.rate_limiter = rate_limiter or RateLimiter()
        self.timeout = timeout
        self.session = requests.Session()

    def get(self, url: str, **kwargs) -> requests.Response:
        """Make GET request with anti-ban protection"""
        self.rate_limiter.wait()

        headers = kwargs.get('headers', {})
        headers['User-Agent'] = UserAgentRotator.get_random()
        kwargs['headers'] = headers

        proxy = self.proxy_manager.get_random_proxy()

        try:
            response = self.session.get(
                url,
                proxies=proxy,
                timeout=self.timeout,
                **kwargs
            )
            response.raise_for_status()
            return response

        except requests.exceptions.ProxyError:
            if proxy:
                self.proxy_manager.mark_proxy_failed(proxy)
            # Retry without proxy
            return self.session.get(url, timeout=self.timeout, **kwargs)

        except Exception as e:
            raise e

    def close(self):
        """Close session"""
        self.session.close()
