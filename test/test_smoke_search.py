"""
Модуль smoke-тестирования функционала поиска на Кинопоиске.

Содержит end-to-end тесты проверки основных сценариев поиска фильмов:
- Поиск по русскому и английскому названиям
- Обработка несуществующих фильмов
- Поведение при пустом поиске
- Исправление опечаток в поисковых запросах

Реализован с использованием:
- Allure для детальной отчетности
- Selenium WebDriver для автоматизации браузера
- Pytest для организации тестов

Входные данные:
- WebDriver instance (через фикстуру browser)
- Конфигурационные параметры из config.Config
- Тестовые данные из config.TEST_DATA

Выходные данные:
- Allure-отчет с шагами выполнения
- Скриншоты при падении тестов
- Assertion ошибки при неудачном выполнении
"""
import pytest
import allure
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config
from search_page import SearchPage


@pytest.mark.ui
@pytest.mark.smoke
class TestKinopoiskSearch:
    """
    Класс для тестирования функционала поиска на сайте Кинопоиск.

    Содержит smoke-тесты основных сценариев поиска фильмов:
    - Поиск по русскому названию
    - Поиск по английскому названию
    - Переход на страницу фильма
    - Поиск несуществующего фильма
    - Пустой поиск
    - Поиск с опечаткой (проверка исправления опечаток)

    Все тесты используют Allure для детальной отчетности и
    WebDriverWait для стабильности ожиданий элементов.
    """

    @allure.feature("Поиск фильмов")
    @allure.story("Основные сценарии поиска")
    def test_search_functionality(self, browser):
        """
        Основной тест проверки функционала поиска фильмов.

        Args:
            browser: Экземпляр WebDriver для управления браузером

        Steps:
            1-2: Поиск и проверка фильма по русскому названию
            3-4: Поиск и проверка фильма по английскому названию
            5: Переход на страницу найденного фильма
            6: Проверка обработки несуществующего фильма
            7: Проверка поведения при пустом поиске
            8: Проверка исправления опечаток в поиске
        """
        search = SearchPage(browser)

        # Шаг 1-2: Поиск и проверка русского названия
        with allure.step("Шаг 1-2: Поиск русского фильма"):
            (search.search(Config.TEST_DATA["russian_film"])
             .verify_result(Config.TEST_DATA["russian_film"]))

        # Шаг 3-4: Поиск и проверка английского названия
        with allure.step("Шаг 3-4: Поиск английского названия"):
            (search.search(Config.TEST_DATA["english_film"])
             .verify_result(
                 Config.TEST_DATA["english_film"],
                 is_english=True
            ))

        # Шаг 5: Переход на страницу фильма
        with allure.step("Шаг 5: Переход на страницу фильма"):
            film_link = browser.find_element(
                By.CSS_SELECTOR,
                "div.search_results > div > div.info > p.name > a"
            )
            film_link.click()
            assert Config.TEST_DATA["russian_film"] in browser.title

        # Шаг 6: Поиск несуществующего фильма
        with allure.step("Шаг 6: Поиск несуществующего фильма"):
            browser.get(Config.BASE_URL)
            search.search(Config.TEST_DATA["wrong_film"])
            assert "ничего не найдено" in browser.page_source

        # Шаг 7: Пустой поиск
        with allure.step("Шаг 7: Пустой поиск"):
            browser.get(Config.BASE_URL)
            search_input = WebDriverWait(
                browser, Config.ELEMENT_TIMEOUT
            ).until(
                EC.presence_of_element_located((By.NAME, "kp_query"))
            )
            search_input.clear()
            search_input.send_keys("\n")  # Отправка Enter с пустым полем
            WebDriverWait(browser, Config.ELEMENT_TIMEOUT).until(
                EC.title_contains("Случайный фильм")
            )
            assert "Случайный фильм" in browser.title

        # Шаг 8: Поиск с опечаткой
        with allure.step("Шаг 8: Поиск с опечаткой"):
            browser.get(Config.BASE_URL)
            (search.search(Config.TEST_DATA["typo_film"])
             .verify_result(Config.TEST_DATA["russian_film"]))
