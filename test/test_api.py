"""
Модуль тестирования API Кинопоиска.

Содержит комплексные тесты для проверки:
- Позитивных сценариев поиска фильмов
- Негативных сценариев (ошибки авторизации, некорректные запросы)
- Функциональности получения случайного фильма

Все тесты используют Allure для формирования детальных отчетов.
"""
import pytest
import allure
import requests
import json
from test_data import TestData
from api_client import KinopoiskAPIClient


class TestKinopoiskAPI:
    """Комплексные тесты API Кинопоиска.

    Атрибуты:
        api_client: Экземпляр клиента для работы с API Кинопоиска

    Методы:
        test_search_positive: Проверка успешных сценариев поиска фильмов
        test_unauthorized_access: Проверка доступа без авторизации
        test_search_negative: Проверка обработки некорректных запросов
        test_random_movie: Проверка получения случайного фильма
    """

    @pytest.fixture(autouse=True)
    def setup(self):
        """Фикстура инициализации тестового окружения."""
        self.api_client = KinopoiskAPIClient()

    @pytest.mark.api
    @allure.feature("Позитивные тесты")
    @allure.story("Поиск фильмов")
    @pytest.mark.positive
    @pytest.mark.parametrize("test_case", TestData.POSITIVE_SEARCH_QUERIES)
    def test_search_positive(self, test_case):
        """Проверка успешных сценариев поиска.

        Args:
            test_case: Словарь с параметрами теста:
                - query: Строка поиска
                - description: Описание теста
                - min_results: Минимальное ожидаемое количество результатов

        Проверки:
            1. Ответ является словарем
            2. Ответ содержит поле 'docs'
            3. Количество результатов >= min_results
        """
        with allure.step(f"Поиск: {test_case['description']}"):
            response_data = self.api_client.search_movies(test_case["query"])

            assert isinstance(response_data, dict), (
                "Ответ должен быть словарем"
            )
            assert "docs" in response_data, (
                "Ответ должен содержать поле 'docs'"
            )
            assert len(response_data["docs"]) >= test_case["min_results"], (
                f"Найдено {len(response_data['docs'])} результатов, "
                f"ожидалось минимум {test_case['min_results']}"
            )

    @pytest.mark.api
    @allure.feature("Негативные тесты")
    @allure.story("Авторизация")
    def test_unauthorized_access(self):
        """Проверка доступа без API-ключа.

        Проверки:
            1. Код ответа 401 (Unauthorized)
            2. Сообщение об ошибке содержит текст о missing token
        """
        with allure.step("Отправка запроса без токена"):
            url = f"{self.api_client.base_url}/search"
            response = requests.get(url, params={"query": "test"})

            assert response.status_code == 401, (
                "Ожидался код статуса 401 для неавторизованного запроса"
            )
            assert (
                response.json()["message"] == "В запросе не указан токен!"
            ), "Неверное сообщение об ошибке"

    @pytest.mark.api
    @allure.feature("Негативные тесты")
    @allure.story("Поиск фильмов")
    @pytest.mark.negative
    @pytest.mark.parametrize("test_case", TestData.NEGATIVE_SEARCH_QUERIES)
    def test_search_negative(self, test_case):
        """Проверка обработки некорректных запросов.

        Args:
            test_case: Словарь с параметрами теста:
                - query: Строка поиска
                - description: Описание теста
                - expect_results: Ожидаются ли результаты
                - check_text_part: Текст для проверки в результатах
                - check_partial_match: Проверять частичное совпадение

        Проверки:
            1. Ответ является словарем
            2. Ответ содержит поле 'docs'
            3. Дополнительные проверки в зависимости от типа теста
        """
        with allure.step(f"Запрос: {test_case['description']}"):
            try:
                response_data = self.api_client.search_movies(
                    test_case["query"])

                allure.attach(
                    json.dumps(response_data, indent=2, ensure_ascii=False),
                    name="Ответ API",
                    attachment_type=allure.attachment_type.JSON
                )

                assert isinstance(response_data, dict), (
                    "Ответ должен быть словарем"
                )
                assert "docs" in response_data, (
                    "Ответ должен содержать поле 'docs'"
                )

                if test_case["query"] == "":
                    assert response_data["docs"], (
                        "Пустой запрос должен возвращать список фильмов"
                    )
                    return

                if test_case.get("expect_results", False):
                    assert response_data["docs"], (
                        "Ожидались результаты"
                    )

                    if "check_text_part" in test_case:
                        text = test_case["check_text_part"].lower()
                        for movie in response_data["docs"]:
                            name = (movie.get("name", "") +
                                    movie.get("alternativeName", "")).lower()
                            assert text in name, (
                                f"Не найден '{text}' в '{name}'"
                            )

                elif test_case.get("check_partial_match", False):
                    if response_data["docs"]:
                        for movie in response_data["docs"]:
                            fields = [
                                movie.get("name", ""),
                                movie.get("alternativeName", ""),
                                " ".join(n["name"]
                                         for n in movie.get("names", []))
                            ]
                            assert any(
                                c in " ".join(fields)
                                for c in test_case["query"]
                            ), "Не найдено соответствие иероглифам"
                else:
                    assert not response_data["docs"], (
                        "Не ожидались результаты"
                    )

            except requests.HTTPError as e:
                if test_case.get("expected_status"):
                    expected_status = test_case["expected_status"]
                    assert e.response.status_code == expected_status, (
                        f"Ожидалась {expected_status} ошибка"
                    )
                else:
                    raise

    @pytest.mark.api
    @allure.feature("Дополнительные тесты")
    @allure.story("Рандомный фильм")
    def test_random_movie(self):
        """Проверка получения случайного фильма.

        Проверки:
            1. Ответ является словарем
            2. Фильм содержит ID
            3. Фильм содержит название (основное или альтернативное)
        """
        with allure.step("Получение случайного фильма"):
            movie_data = self.api_client.get_random_movie()

            assert isinstance(movie_data, dict), (
                "Ответ должен быть словарем"
            )
            assert movie_data.get("id"), (
                "Фильм должен содержать ID"
            )
            assert (
                movie_data.get("name") or movie_data.get("alternativeName")
            ), "Нет названия фильма"
