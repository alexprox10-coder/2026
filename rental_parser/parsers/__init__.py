"""
Parsers for rental property platforms
"""
from .cian_parser import CianParser
from .yandex_parser import YandexRealtyParser
from .avito_parser import AvitoParser

__all__ = ['CianParser', 'YandexRealtyParser', 'AvitoParser']
