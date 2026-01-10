"""Модуль для парсинга данных с сайтов компаний"""
import logging
import re
import requests
from bs4 import BeautifulSoup
from typing import Dict, Any, List, Optional
from urllib.parse import urljoin, urlparse

logger = logging.getLogger(__name__)


class WebScraper:
    """Парсер для извлечения данных с сайтов компаний"""

    def __init__(self):
        """Инициализация парсера"""
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        self.timeout = 10

    def scrape_company_info(self, url: str) -> Dict[str, Any]:
        """
        Парсинг информации о компании с сайта

        Args:
            url: URL сайта компании

        Returns:
            Словарь с данными компании
        """
        info = {
            'сайт': url,
            'название': '',
            'описание': '',
            'email': '',
            'телефон': '',
            'адрес': '',
            'услуги': '',
            'контактное_лицо': '',
            'соцсети': ''
        }

        try:
            # Нормализуем URL
            if not url.startswith(('http://', 'https://')):
                url = 'https://' + url

            # Получаем содержимое страницы
            response = requests.get(url, headers=self.headers, timeout=self.timeout)
            response.raise_for_status()
            response.encoding = response.apparent_encoding

            soup = BeautifulSoup(response.text, 'html.parser')

            # Извлекаем название
            info['название'] = self._extract_company_name(soup, url)

            # Извлекаем описание
            info['описание'] = self._extract_description(soup)

            # Извлекаем контактную информацию
            info['email'] = self._extract_emails(soup, url)
            info['телефон'] = self._extract_phones(soup)
            info['адрес'] = self._extract_address(soup)

            # Извлекаем услуги
            info['услуги'] = self._extract_services(soup)

            # Извлекаем социальные сети
            info['соцсети'] = self._extract_social_media(soup)

            logger.info(f"Успешно собраны данные с сайта: {url}")

        except requests.RequestException as e:
            logger.error(f"Ошибка при запросе к {url}: {e}")
        except Exception as e:
            logger.error(f"Ошибка при парсинге {url}: {e}")

        return info

    def _extract_company_name(self, soup: BeautifulSoup, url: str) -> str:
        """Извлечь название компании"""
        # Пытаемся найти в title
        if soup.title and soup.title.string:
            return soup.title.string.strip()

        # Пытаемся найти в h1
        h1 = soup.find('h1')
        if h1:
            return h1.get_text(strip=True)

        # Пытаемся найти в meta
        meta_title = soup.find('meta', property='og:site_name')
        if meta_title and meta_title.get('content'):
            return meta_title['content'].strip()

        # Используем домен как название
        domain = urlparse(url).netloc
        return domain.replace('www.', '')

    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Извлечь описание компании"""
        # Meta description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc and meta_desc.get('content'):
            return meta_desc['content'].strip()

        # OG description
        og_desc = soup.find('meta', property='og:description')
        if og_desc and og_desc.get('content'):
            return og_desc['content'].strip()

        # Ищем в основном контенте
        for tag in soup.find_all(['p', 'div'], class_=re.compile(r'about|description|intro', re.I)):
            text = tag.get_text(strip=True)
            if len(text) > 50:
                return text[:500]

        return ''

    def _extract_emails(self, soup: BeautifulSoup, url: str) -> str:
        """Извлечь email адреса"""
        emails = set()

        # Поиск в тексте страницы
        text = soup.get_text()
        email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
        found_emails = re.findall(email_pattern, text)
        emails.update(found_emails)

        # Поиск в ссылках mailto
        for link in soup.find_all('a', href=re.compile(r'^mailto:')):
            email = link['href'].replace('mailto:', '').split('?')[0]
            emails.add(email)

        # Фильтруем спам и общие адреса
        spam_patterns = ['example.com', 'test.com', 'domain.com', 'noreply', 'no-reply']
        emails = [e for e in emails if not any(spam in e.lower() for spam in spam_patterns)]

        return ', '.join(sorted(emails)[:3])  # Возвращаем первые 3

    def _extract_phones(self, soup: BeautifulSoup) -> str:
        """Извлечь номера телефонов"""
        phones = set()

        # Поиск в тексте
        text = soup.get_text()

        # Российские форматы телефонов
        phone_patterns = [
            r'\+7[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}',
            r'8[\s-]?\(?\d{3}\)?[\s-]?\d{3}[\s-]?\d{2}[\s-]?\d{2}',
            r'\+7[\s-]?\d{10}',
            r'8[\s-]?\d{10}'
        ]

        for pattern in phone_patterns:
            found = re.findall(pattern, text)
            phones.update(found)

        # Поиск в ссылках tel:
        for link in soup.find_all('a', href=re.compile(r'^tel:')):
            phone = link['href'].replace('tel:', '').strip()
            phones.add(phone)

        return ', '.join(sorted(phones)[:3])  # Возвращаем первые 3

    def _extract_address(self, soup: BeautifulSoup) -> str:
        """Извлечь адрес"""
        # Поиск по классам/id
        address_patterns = ['address', 'addr', 'location', 'контакты']

        for pattern in address_patterns:
            for tag in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                text = tag.get_text(strip=True)
                if len(text) > 10 and len(text) < 200:
                    return text

            for tag in soup.find_all(attrs={'id': re.compile(pattern, re.I)}):
                text = tag.get_text(strip=True)
                if len(text) > 10 and len(text) < 200:
                    return text

        # Поиск микроразметки
        address_tag = soup.find(attrs={'itemprop': 'address'})
        if address_tag:
            return address_tag.get_text(strip=True)

        return ''

    def _extract_services(self, soup: BeautifulSoup) -> str:
        """Извлечь список услуг"""
        services = []

        # Поиск по классам
        service_patterns = ['service', 'услуг', 'product', 'offer']

        for pattern in service_patterns:
            for tag in soup.find_all(attrs={'class': re.compile(pattern, re.I)}):
                # Ищем списки
                lists = tag.find_all(['ul', 'ol'])
                for lst in lists:
                    items = [li.get_text(strip=True) for li in lst.find_all('li')]
                    services.extend(items)

        # Убираем дубликаты и возвращаем первые 10
        unique_services = list(dict.fromkeys(services))
        return ', '.join(unique_services[:10])

    def _extract_social_media(self, soup: BeautifulSoup) -> str:
        """Извлечь ссылки на социальные сети"""
        social_links = set()

        social_domains = [
            'facebook.com', 'instagram.com', 'vk.com', 'ok.ru',
            'twitter.com', 'linkedin.com', 'youtube.com', 't.me',
            'telegram.me', 'whatsapp.com'
        ]

        for link in soup.find_all('a', href=True):
            href = link['href']
            for domain in social_domains:
                if domain in href:
                    social_links.add(href)

        return ', '.join(sorted(social_links))

    def scrape_contact_page(self, base_url: str) -> Dict[str, Any]:
        """
        Попытка найти и спарсить страницу контактов

        Args:
            base_url: Базовый URL сайта

        Returns:
            Словарь с дополнительными контактными данными
        """
        contact_pages = [
            '/contacts', '/contact', '/kontakty', '/about',
            '/о-компании', '/контакты'
        ]

        for path in contact_pages:
            try:
                url = urljoin(base_url, path)
                response = requests.get(url, headers=self.headers, timeout=self.timeout)

                if response.status_code == 200:
                    soup = BeautifulSoup(response.text, 'html.parser')
                    return {
                        'email': self._extract_emails(soup, url),
                        'телефон': self._extract_phones(soup),
                        'адрес': self._extract_address(soup)
                    }
            except:
                continue

        return {}
