"""
Модуль для взаимодействия с API Кинопоиска.

Предоставляет удобный интерфейс для работы с API Кинопоиска
(https://api.kinopoisk.dev), включая поиск фильмов и получение
случайных фильмов. Все запросы автоматически включают
авторизацию через API-ключ из настроек приложения.

Пример использования:
    >>> client = KinopoiskAPIClient()
    >>> result = client.search_movies("Гарри Поттер")
    >>> random_movie = client.get_random_movie()
"""

import requests
from settings import settings


class KinopoiskAPIClient:
    """Клиент для работы с API Кинопоиска версии 1.4.

    Позволяет взаимодействовать с API Кинопоиска для получения
    информации о фильмах. Все методы обрабатывают базовые ошибки
    сети и API.

    Особенности:
        - Автоматическая авторизация по API-ключу
        - Встроенная обработка HTTP-ошибок
        - Поддержка пагинации при поиске
        - Возвращает данные в формате JSON
    """

    def __init__(self) -> None:
        """Инициализирует клиент API с настройками из конфигурации.

        Загружает:
            - Базовый URL API (например,
            'https://api.kinopoisk.dev/v1.4/movie')
            - API-ключ для авторизации запросов

        Пример:
            >>> client = KinopoiskAPIClient()
            >>> print(client.base_url)
            'https://api.kinopoisk.dev/v1.4/movie'
        """
        self.base_url = settings.API_URL
        self.headers = {
            "accept": "application/json",
            "X-API-KEY": settings.API_KEY
        }

    def search_movies(
        self,
        query: str,
        page: int = 1,
        limit: int = 10
    ) -> dict[str, int | list]:
        """Ищет фильмы по названию с возможностью пагинации.

        Отправляет GET-запрос к /search endpoint API Кинопоиска.

        Аргументы:
            query: Строка для поиска (например, "Гарри Поттер")
            page: Номер страницы результатов (начинается с 1)
            limit: Максимальное количество результатов на странице (1-50)

        Возвращает:
            Словарь с результатами в формате:
            {
                "page": 1,                 # Текущая страница
                "total": 42,               # Всего найдено фильмов
                "movies": [{...}, {...}]    # Список фильмов
            }

        Исключения:
            requests.HTTPError: Если API возвращает ошибку (4xx или 5xx)
            requests.RequestException: При проблемах с сетью
        """
        url = f"{self.base_url}/search"
        params = {
            "query": query,
            "page": page,
            "limit": min(limit, 50)  # API ограничивает максимум 50
        }
        response = requests.get(
            url,
            headers=self.headers,
            params=params
        )
        response.raise_for_status()
        return response.json()

    def get_random_movie(self) -> dict[str, int | str | list] | None:
        """Получает один случайный фильм из базы Кинопоиска.

        Использует /random endpoint API. В случае ошибки возвращает None.

        Возвращает:
            Словарь с полной информацией о фильме или None при ошибке.
            Пример структуры:
            {
                "id": 123456,
                "name": "Интерстеллар",
                "year": 2014,
                "rating": {"kp": 8.6},
                "genres": [{"name": "фантастика"}, ...]
            }
        """
        url = f"{self.base_url}/random"
        try:
            response = requests.get(url, headers=self.headers)
            response.raise_for_status()
            return response.json()
        except requests.RequestException as e:
            print(f"Ошибка при получении фильма: {e}")
            return None
