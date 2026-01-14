"""
Модуль Page Object для страницы поиска на кинопортале.

Содержит класс SearchPage с методами для взаимодействия с элементами
страницы поиска и проверки результатов. Реализует паттерн Page Object Model
для улучшения читаемости и поддержки автоматизированных тестов.

Основные функции:
- Инициализация страницы и переход на базовый URL
- Выполнение поисковых запросов
- Верификация результатов поиска (русские и английские названия)
- Обработка различных селекторов для мультиязычного контента

Входные данные:
- WebDriver instance для управления браузером
- Поисковые запросы в виде строк
- Ожидаемые результаты для проверки

Выходные данные:
- Self reference для цепочки вызовов методов (fluent interface)
- Assertion результаты проверок
"""

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from config import Config


class SearchPage:
    """Page Object класс для страницы поиска фильмов."""

    def __init__(self, browser):
        """
        Инициализация страницы поиска.

        Args:
            browser: WebDriver instance для управления браузером

        Returns:
            None: Производит инициализацию объекта и переход на базовый URL
        """
        self.browser = browser
        self.browser.get(Config.BASE_URL)

    def search(self, query: str):
        """
        Выполняет поиск фильма по заданному запросу.

        Метод выполняет следующие действия:
        - Ожидает появления поисковой строки на странице
        - Очищает поле ввода от предыдущих значений
        - Вводит переданный поисковый запрос
        - Отправляет форму поиска

        Args:
            query (str): Поисковый запрос (название фильма)

        Returns:
            SearchPage: Self reference для method chaining

        Raises:
            TimeoutException:
            Если поисковая строка не найдена в течение таймаута
        """
        search_input = WebDriverWait(
            self.browser, Config.ELEMENT_TIMEOUT
        ).until(
            EC.presence_of_element_located((By.NAME, "kp_query"))
        )
        search_input.clear()
        search_input.send_keys(query)
        search_input.submit()
        return self

    def verify_result(self, expected_text: str, is_english: bool = False):
        """
        Проверяет наличие ожидаемого результата в поисковой выдаче.

        В зависимости от флага is_english использует разные стратегии проверки:
        - Для русских названий: проверяет основной заголовок
        - Для английских названий: проверяет альтернативные названия

        Args:
            expected_text (str): Ожидаемый текст в результатах поиска
            is_english (bool, optional): Флаг для английских названий.
                                        Defaults to False.

        Returns:
            SearchPage: Self reference для method chaining

        Raises:
            AssertionError: Если ожидаемый текст не найден в результатах
            TimeoutException: Если элементы не найдены в течение таймаута
        """
        if is_english:
            self._verify_english_result(expected_text)
        else:
            result = WebDriverWait(
                self.browser, Config.ELEMENT_TIMEOUT
            ).until(
                EC.presence_of_element_located((
                    By.CSS_SELECTOR,
                    "div.search_results > div > div.info > p.name > a"
                ))
            )
            assert expected_text in result.text
        return self

    def _verify_english_result(self, expected_result: str):
        """
        Проверяет наличие английского названия в результатах поиска.

        Использует несколько возможных локаторов для поиска альтернативных
        названий на случай изменения структуры страницы.

        Args:
            expected_result (str): Ожидаемое английское название

        Raises:
            AssertionError: Если английское название не найдено ни в одном
                           из возможных мест
            TimeoutException: Если ни один из локаторов не сработал
        """
        possible_locators = [
            (By.CSS_SELECTOR,
             "div.search_results > div > div.info > p.alternativeName"),
            (By.CSS_SELECTOR, "span.alternativeName"),
            (By.XPATH, "//*[contains(@class, 'alternativeName')]")
        ]

        for locator in possible_locators:
            try:
                element = WebDriverWait(self.browser, 3).until(
                    EC.presence_of_element_located(locator))
                if expected_result in element.text:
                    return
            except Exception:
                continue

        assert expected_result in self.browser.page_source, (
            f"Английское название '{expected_result}' не найдено"
        )
