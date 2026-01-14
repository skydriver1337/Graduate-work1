"""
Модуль с тестовыми данными для API-запросов к Кинопоиску.

Содержит готовые тест-кейсы для проверки:
1. Поиска фильмов по различным типам запросов:
   - Точные названия
   - Частичные совпадения
   - Специальные символы
   - Unicode-строки
   - Граничные случаи

2. Проверки эндпоинта получения случайного фильма.

Все тестовые данные содержат:
- Непосредственно тестовый запрос (query)
- Четкое описание цели теста (description)
- Явные ожидания от API (min_results, expect_results и др.)
- Дополнительные параметры для валидации ответов

Пример использования в тестах:
    >>> test_case = TestData.POSITIVE_SEARCH_QUERIES[0]
    >>> assert len(search_results) >= test_case["min_results"]
"""


class TestData:
    """Класс для хранения тестовых данных с явными ожиданиями поведения API."""

    """
    Содержит три группы данных:
    1. POSITIVE_SEARCH_QUERIES - валидные запросы с ожидаемыми результатами
    2. NEGATIVE_SEARCH_QUERIES -
    проблемные запросы для проверки обработки ошибок
    3. RANDOM_MOVIE_ENDPOINT - константа для тестирования эндпоинта /random

    Структура каждого тест-кейса:
    {
        "query": str,               # Строка запроса
        "description": str,         # Пояснение цели теста
        "min_results": int,         # Минимальное ожидаемое кол-во результатов
        "expect_results": bool,     # Ожидаем ли вообще результаты
        "check_text_part": str,     # Какая строка должна быть в результатах
        "check_partial_match": bool # Нужно ли проверять частичное совпадение
    }
    """
    # Позитивные тесты (ожидаем найденные фильмы)
    POSITIVE_SEARCH_QUERIES = [
        {
            "query": "В списках не значился",
            "description": "Точное название - проверка точного совпадения",
            "min_results": 1  # Ожидаем хотя бы 1 результат
        },
        {
            "query": "Novocaine",
            "description": "Название на английском",
            "min_results": 1
        },
        {
            "query": "Годзилла 1998",
            "description": "Название с годом",
            "min_results": 1
        },
        {
            "query": "Терми",
            "description": "Частичное название",
            "min_results": 3  # Ожидаем несколько вариантов
        }
    ]

    # Негативные тесты с явными ожиданиями
    NEGATIVE_SEARCH_QUERIES = [
        # Спецсимволы
        {
            "query": "@#%",
            "description": "Только спецсимволы",
            "expect_results": True  # Ожидаем ли результаты для такого запроса
        },
        {
            "query": "@#%Годзилла",
            "description": "Спецсимволы в начале",
            "expect_results": True,
            "check_text_part": "Годзилла"
        },
        {
            "query": "Годзилла@",
            "description": "Спецсимволы в конце",
            "expect_results": True,
            "check_text_part": "Годзилла"
        },

        # Unicode
        {
            "query": "ó♝▼☥❋",
            "description": "Юникод-символы",
            "expect_results": False
        },

        # Иероглифы
        {
            "query": "龙之剑",
            "description": "Китайские иероглифы",
            "check_partial_match": True
        },

        # Пустой запрос
        {
            "query": "",
            "description": "Пустой запрос - возвращает популярные фильмы",
            "expect_results": True
        },

        # Длинный запрос
        {
            "query": "a"*256,
            "description": "Длинный запрос (>255 символов)",
            "expect_results": False
        }
    ]

    # Рандомный фильм
    RANDOM_MOVIE_ENDPOINT = "/random"
