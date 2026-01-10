"""Модуль для работы с Google Maps API"""
import logging
import requests
from typing import List, Dict, Any, Optional
from config.settings import GOOGLE_MAPS_API_KEY

logger = logging.getLogger(__name__)


class GoogleMapsParser:
    """Парсер для получения данных из Google Maps"""

    def __init__(self):
        """Инициализация парсера"""
        if not GOOGLE_MAPS_API_KEY:
            logger.warning("Google Maps API ключ не настроен")
            self.api_key = None
        else:
            self.api_key = GOOGLE_MAPS_API_KEY

        self.base_url = "https://maps.googleapis.com/maps/api"

    def search_places(self, query: str, location: str = None, radius: int = 50000) -> List[Dict[str, Any]]:
        """
        Поиск мест по запросу

        Args:
            query: Поисковый запрос (например, "стоматология")
            location: Локация для поиска (например, "Москва")
            radius: Радиус поиска в метрах

        Returns:
            Список найденных мест с данными
        """
        if not self.api_key:
            logger.error("API ключ не настроен")
            return []

        places = []

        try:
            # Если указана локация, сначала получаем её координаты
            if location:
                geocode_url = f"{self.base_url}/geocode/json"
                geocode_params = {
                    'address': location,
                    'key': self.api_key
                }

                geocode_response = requests.get(geocode_url, params=geocode_params, timeout=10)
                geocode_data = geocode_response.json()

                if geocode_data['status'] == 'OK':
                    lat = geocode_data['results'][0]['geometry']['location']['lat']
                    lng = geocode_data['results'][0]['geometry']['location']['lng']
                    location_str = f"{lat},{lng}"
                else:
                    logger.warning(f"Не удалось геокодировать локацию: {location}")
                    location_str = None
            else:
                location_str = None

            # Поиск мест
            search_url = f"{self.base_url}/place/textsearch/json"
            search_params = {
                'query': f"{query} {location}" if location else query,
                'key': self.api_key,
                'language': 'ru'
            }

            if location_str:
                search_params['location'] = location_str
                search_params['radius'] = radius

            response = requests.get(search_url, params=search_params, timeout=10)
            data = response.json()

            if data['status'] == 'OK':
                for place in data['results']:
                    place_info = self._extract_place_info(place)
                    if place_info:
                        places.append(place_info)

                # Обработка пагинации (если есть следующая страница)
                while 'next_page_token' in data and len(places) < 60:  # Ограничение на 60 мест
                    import time
                    time.sleep(2)  # Google требует задержку перед использованием токена

                    next_params = {
                        'pagetoken': data['next_page_token'],
                        'key': self.api_key
                    }

                    response = requests.get(search_url, params=next_params, timeout=10)
                    data = response.json()

                    if data['status'] == 'OK':
                        for place in data['results']:
                            place_info = self._extract_place_info(place)
                            if place_info:
                                places.append(place_info)

                logger.info(f"Найдено {len(places)} мест по запросу: {query}")

            else:
                logger.warning(f"Google Maps API вернул статус: {data['status']}")

        except Exception as e:
            logger.error(f"Ошибка при поиске мест: {e}")

        return places

    def get_place_details(self, place_id: str) -> Optional[Dict[str, Any]]:
        """
        Получить детальную информацию о месте

        Args:
            place_id: ID места в Google Maps

        Returns:
            Словарь с детальной информацией или None
        """
        if not self.api_key:
            logger.error("API ключ не настроен")
            return None

        try:
            details_url = f"{self.base_url}/place/details/json"
            params = {
                'place_id': place_id,
                'fields': 'name,formatted_address,formatted_phone_number,website,opening_hours,rating,user_ratings_total',
                'key': self.api_key,
                'language': 'ru'
            }

            response = requests.get(details_url, params=params, timeout=10)
            data = response.json()

            if data['status'] == 'OK':
                return data['result']
            else:
                logger.warning(f"Не удалось получить детали места: {data['status']}")
                return None

        except Exception as e:
            logger.error(f"Ошибка при получении деталей места: {e}")
            return None

    def _extract_place_info(self, place: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Извлечь информацию о месте из ответа API

        Args:
            place: Данные места из API

        Returns:
            Словарь с информацией о месте
        """
        try:
            # Получаем детальную информацию
            place_id = place.get('place_id')
            details = self.get_place_details(place_id) if place_id else {}

            info = {
                'название': place.get('name', ''),
                'адрес': place.get('formatted_address', ''),
                'телефон': details.get('formatted_phone_number', '') if details else '',
                'сайт': details.get('website', '') if details else '',
                'рейтинг': place.get('rating', 0),
                'категория': ', '.join(place.get('types', [])),
                'place_id': place_id
            }

            # Проверяем наличие сайта
            if not info['сайт']:
                logger.debug(f"У места {info['название']} нет сайта")

            return info

        except Exception as e:
            logger.error(f"Ошибка при извлечении информации о месте: {e}")
            return None
