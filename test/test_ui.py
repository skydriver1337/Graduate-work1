"""
UI тесты для функциональности поиска на Кинопоиске.

Содержит тесты для проверки различных сценариев поиска фильмов.
Все тесты используют фикстуру browser из conftest.py и конфигурацию
из config.py.
"""

import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from config import Config


class TestKinopoiskSearch:
    """Класс тестов для функциональности поиска на Кинопоиске."""

    def search_for_film(self, browser, search_query):
        """
        Выполняет поиск фильма по запросу.

        Args:
            browser: Экземпляр WebDriver
            search_query: Строка для поиска
        """
        wait = WebDriverWait(browser, Config.ELEMENT_TIMEOUT)
        try:
            search_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            )
            search_input.clear()
            search_input.send_keys(search_query)

            # Нажимаем Enter для поиска
            search_input.send_keys("\n")

            # Ожидание появления результатов поиска

            wait.until(EC.presence_of_element_located((
                By.CSS_SELECTOR,
                ".search_results, .block_left, [data-test*='search-results']"
            )))

            # Дополнительная задержка
            # Неявное ожидание загрузки элементов
            wait.until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    ".search_results .name, .block_left .name"
                )))

        except TimeoutException:
            pytest.fail(
                f"Не удалось выполнить поиск для запроса: {search_query}")

    def verify_search_result(self, browser, expected_title, position=0,
                             partial_match=True):
        """
        Проверяет, что в результатах поиска есть ожидаемый заголовок.

        Args:
            browser: Экземпляр WebDriver
            expected_title: Ожидаемый заголовок фильма
            position: Позиция в списке результатов (по умолчанию 0 - первый)
            partial_match: Если True, ищет частичное совпадение, иначе точное

        Returns:
            bool: True если найден, False если нет
        """
        wait = WebDriverWait(browser, Config.ELEMENT_TIMEOUT)
        try:
            # Поиск всех результатов с разными селекторами
            selectors = [
                "div.search_results > div > div.info > p.name > a",
                ".search_results .name",
                ".block_left .name",
                "[data-test*='film-title']",
                "h1.name",
                ".film-name"
            ]

            for selector in selectors:
                try:
                    results = wait.until(
                        EC.presence_of_all_elements_located(
                            (By.CSS_SELECTOR, selector))
                    )
                    if results and len(results) > position:
                        actual_title = results[position].text.strip()
                        if partial_match:
                            # Частичное совпадение
                            expected_lower = expected_title.lower()
                            actual_lower = actual_title.lower()
                            return expected_lower in actual_lower

                        else:
                            # Точное совпадение
                            expected_normalized = expected_title.lower()
                            actual_normalized = actual_title.lower()
                            return expected_normalized == actual_normalized

                except (TimeoutException, NoSuchElementException):
                    continue

            return False

        except Exception:
            return False

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Точное совпадение названия")
    def test_fpk1_exact_match_search(self, browser):
        """FPK 1: Точное совпадение названия."""
        browser.get(Config.BASE_URL)

        search_query = "В списках не значился"
        self.search_for_film(browser, search_query)

        assert self.verify_search_result(browser, search_query), \
            f"Фильм '{search_query}' не найден первым в результатах поиска"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поиск на русском языке")
    def test_fpk2_russian_search(self, browser):
        """FPK 2: Поиск на русском языке."""
        browser.get(Config.BASE_URL)

        search_query = Config.get_test_data("russian_film")
        self.search_for_film(browser, search_query)

        assert self.verify_search_result(browser, search_query), \
            f"Фильм '{search_query}' не найден первым в результатах поиска"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поиск на английском языке")
    def test_fpk3_english_search(self, browser):
        """FPK 3: Поиск на английском языке."""
        browser.get(Config.BASE_URL)

        english_query = Config.get_test_data("english_film")
        russian_expected = Config.get_test_data("russian_film")

        self.search_for_film(browser, english_query)

        assert self.verify_search_result(browser, russian_expected), \
            f"Фильм '{russian_expected}' не найден при поиске " \
            f"по английскому названию '{english_query}'"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Частичное совпадение названия")
    def test_fpk4_partial_match(self, browser):
        """FPK 4: Частичное совпадение названия."""
        browser.get(Config.BASE_URL)

        search_query = "Три"

        self.search_for_film(browser, search_query)

        # Проверяем, что в результатах поиска есть названия, содержащие "Три"
        wait = WebDriverWait(browser, Config.ELEMENT_TIMEOUT)
        try:
            # Получаем все результаты поиска
            results = wait.until(
                EC.presence_of_all_elements_located((
                    By.CSS_SELECTOR,
                    ".search_results .name, .block_left .name, "
                    "[data-test*='film-title']"
                ))
            )

            # Проверяем, что есть хотя бы несколько результатов
            assert len(results) > 0, "Нет результатов поиска"

            # Считаем сколько результатов содержат "Три"
            results_with_tri = 0
            tri_results = []

            for result in results:
                result_text = result.text.strip()
                if 'три' in result_text.lower():  # Проверяем в нижнем регистре
                    results_with_tri += 1
                    tri_results.append(result_text)

            print(f"Найдено результатов с 'Три': {results_with_tri}")
            for i, result in enumerate(tri_results):
                print(f"Результат с 'Три' {i}: '{result}'")

            # Проверяем, что хотя бы 3 результата содержат "Три"
            assert results_with_tri >= 3, (
                f"Мало результатов с 'Три'. Найдено: {results_with_tri}, "
                f"ожидалось минимум 3. Все результаты: "
                f"{[r.text for r in results[:5]]}"
            )

        except TimeoutException:
            pytest.fail("Не удалось получить результаты поиска")

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поиск с указанием года")
    def test_fpk5_search_with_year(self, browser):
        """FPK 5: Поиск с указанием года."""
        browser.get(Config.BASE_URL)

        search_query = "Годзилла 1998"
        expected_film = "Годзилла"

        self.search_for_film(browser, search_query)

        # Проверяем, что найден правильный фильм

        assert self.verify_search_result(browser, expected_film), (
            f"Фильм '{expected_film}' не найден первым "
            f"при поиске '{search_query}'"
        )

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поиск сериалов")
    def test_fpk6_series_search(self, browser):
        """FPK 6: Поиск сериалов."""
        browser.get(Config.BASE_URL)

        search_query = "Звездный путь"
        expected_series = "Звездный путь"

        self.search_for_film(browser, search_query)

        assert self.verify_search_result(browser, expected_series), \
            f"Сериал '{expected_series}' не найден в результатах поиска"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поиск с учетом регистра")
    def test_fpk7_case_insensitive_search(self, browser):
        """FPK 7: Поиск с учетом регистра."""
        browser.get(Config.BASE_URL)

        search_query = "сТаЛкер"
        expected_film = "Сталкер"

        self.search_for_film(browser, search_query)

        assert self.verify_search_result(browser, expected_film), \
            f"Фильм '{expected_film}' не найден при поиске " \
            f"с разным регистром '{search_query}'"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Работа автоподсказок")
    def test_fpk8_autosuggestions(self, browser):
        """FPK 8: Работа автоподсказок."""
        browser.get(Config.BASE_URL)
        wait = WebDriverWait(browser, Config.ELEMENT_TIMEOUT)

        try:
            search_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            )
            search_input.clear()
            search_input.send_keys("Т")

            # Ожидание появления автоподсказок
            suggestions = wait.until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    ".kinopoisk-header-suggest__groups-container, "
                    ".suggestions-container, .autocomplete, "
                    "[data-test*='suggest']"
                ))
            )

            # Проверяем, что подсказки начинаются на букву "Т"
            suggestion_items = suggestions.find_elements(
                By.CSS_SELECTOR,
                ".kinopoisk-header-suggest-item__title, .suggestion-item, "
                "li, [data-test*='suggest-item']"
            )

            assert len(suggestion_items) > 0, "Автоподсказки не появились"

            # Проверяем, что ВСЕ подсказки начинаются на "Т" (кириллическую)
            for item in suggestion_items:
                item_text = item.text.strip()
                if item_text:  # Проверяем только непустые элементы
                    assert item_text.lower().startswith('т'), \
                        f"Подсказка '{item_text}' не начинается на букву 'Т'"

        except TimeoutException:
            pytest.fail("Автоподсказки не появились в течение таймаута")

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Поддержка специальных знаков")
    def test_fpk9_special_characters(self, browser):
        """FPK 9: Поддержка специальных знаков."""
        browser.get(Config.BASE_URL)

        search_query = "Человек-Паук"
        expected_film = "Человек-паук"

        self.search_for_film(browser, search_query)

        assert self.verify_search_result(browser, expected_film), \
            f"Фильм '{expected_film}' не найден при поиске " \
            f"с дефисом '{search_query}'"

    @pytest.mark.ui
    @allure.feature("Поиск фильмов")
    @allure.story("Пустой запрос")
    def test_fpk10_empty_search(self, browser):
        """FPK 10: Пустой запрос."""
        browser.get(Config.BASE_URL)
        wait = WebDriverWait(browser, Config.ELEMENT_TIMEOUT)

        try:
            # Находим поле поиска и оставляем пустым
            search_input = wait.until(
                EC.element_to_be_clickable((By.NAME, "kp_query"))
            )
            search_input.clear()

            # Нажимаем Enter в пустом поле
            search_input.send_keys("\n")

            # Ожидаем перехода на страницу /chance/
            wait.until(
                EC.url_contains("/chance/")
            )

            # Проверяем, что открылась страница "Случайный фильм"
            current_url = browser.current_url
            assert "/chance/" in current_url, \
                "Не открылась страница случайного фильма после пустого поиска"

            # Проверяем, что есть заголовок страницы
            page_title = browser.title
            assert page_title, \
                "Не найден заголовок страницы после пустого поиска"

        except TimeoutException:
            pytest.fail("Не удалось выполнить пустой поиск")
