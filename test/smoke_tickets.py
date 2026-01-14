"""
Модуль smoke-тестирования функционала покупки билетов на Кинопоиске.

Содержит end-to-end тест проверки полного цикла покупки билетов:
от выбора фильма до выбора сеанса в кинотеатре. Реализован с использованием
Allure для детальной отчетности и
Selenium WebDriver для автоматизации браузера.

Основные тестируемые функции:
- Навигация по разделам сайта
- Выбор города (Москва)
- Выбор фильма из списка
- Выбор кинотеатра и сеанса
- Работа с всплывающими окнами и iframe

Входные данные:
- WebDriver instance (через фикстуру browser)
- Конфигурационные параметры из config.Config

Выходные данные:
- Allure-отчет с детализированными шагами выполнения
- Скриншоты при падении теста
- Assertion ошибки при неудачном выполнении шагов
"""

import pytest
import allure
from config import Config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains


@pytest.mark.ui
@pytest.mark.smoke
class TestKinopoiskTickets:
    """Тестовый класс для проверки функционала покупки билетов."""

    @allure.feature("KR-34 / Smoke testing Kinopoisk")
    @allure.story("Подбор и покупка билетов в кино")
    @allure.title("Полный цикл покупки билетов в кинотеатр")
    def test_first_steps(self, browser):
        """
        End-to-end тест полного цикла покупки билетов.

        Args:
            browser: WebDriver instance для управления браузером

        Raises:
            AssertionError: Если любой из шагов теста завершается неудачно
            TimeoutException: Если элементы не найдены в течение таймаута

        Steps:
            1. Переход в раздел 'Билеты в кино'
            2. Выбор города Москва
            3. Выбор первого фильма и переход к покупке
            4. Выбор кинотеатра и сеанса
        """
        with allure.step(
            "Step 1: Зайти на сайт Кинопоиск и перейти в раздел Билеты в кино"
        ):
            self._navigate_to_tickets_section(browser)

        with allure.step("Step 2: Проверить/выбрать город Москва"):
            self._select_city_moscow(browser)

        with allure.step(
            "Step 3: Выбрать первый фильм из списка и нажать 'Купить билеты'"
        ):
            self._select_first_movie(browser)

        with allure.step("Step 4: Выбрать кинотеатр и сеанс"):
            self._select_cinema_and_session(browser)

    def _navigate_to_tickets_section(self, browser):
        """
        Навигация в раздел 'Билеты в кино'.

        Args:
            browser: WebDriver instance

        Raises:
            AssertionError: Если не удалось найти или кликнуть кнопку билетов
        """
        browser.get(Config.BASE_URL)

        tickets_btn = WebDriverWait(browser, Config.ELEMENT_TIMEOUT).until(
            EC.element_to_be_clickable((
                By.XPATH,
                "//a[contains(@class, 'kinopoisk-header-featured-menu__item') "
                "and contains(., 'Билеты в кино')]"
            ))
        )
        tickets_btn.click()

    def _select_city_moscow(self, browser):
        """
        Установка города Москва в селекторе города.

        Args:
            browser: WebDriver instance

        Raises:
            AssertionError: Если не удалось установить город Москва
        """
        city_selector = WebDriverWait(browser, Config.ELEMENT_TIMEOUT).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//details[@data-tid='ba5b39a6']//"
                "div[contains(@class, 'styles_selectButton__idpGM')]"
            ))
        )

        current_city = city_selector.find_element(
            By.XPATH,
            ".//span[contains(@class, 'styles_buttonCaption__llWnp')]"
        ).text

        if current_city != "Москва":
            city_selector.click()

            moscow_option = WebDriverWait(
                browser, Config.ELEMENT_TIMEOUT
            ).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//div[contains(@class, 'styles_body__r29th')]//"
                    "*[contains(text(), 'Москва')]"
                ))
            )
            moscow_option.click()

    def _select_first_movie(self, browser):
        """
        Выбор первого фильма из списка и переход к покупке.

        Args:
            browser: WebDriver instance

        Returns:
            str: Название выбранного фильма

        Raises:
            AssertionError: Если не удалось выбрать фильм
        """
        movies_container = WebDriverWait(
            browser, Config.SEARCH_TIMEOUT
        ).until(
            EC.presence_of_element_located((
                By.XPATH,
                "//div[contains(@class, 'styles_contentSlot__e6vek')]"
            ))
        )

        first_movie = WebDriverWait(
            movies_container, Config.ELEMENT_TIMEOUT
        ).until(
            EC.presence_of_element_located((
                By.XPATH,
                ".//div[contains(@class, 'styles_root__dtojy') and "
                "@data-test-id='movie-list-item'][1]"
            ))
        )

        movie_title = first_movie.find_element(
            By.XPATH,
            ".//span[contains(@class, 'styles_mainTitle__RHG2S')]"
        ).text

        ActionChains(browser).move_to_element(first_movie).perform()

        buy_button = WebDriverWait(
            first_movie, Config.ELEMENT_TIMEOUT
        ).until(
            EC.element_to_be_clickable((
                By.XPATH,
                ".//a[contains(@class, 'style_button__Awsrq') and "
                "contains(., 'Купить билеты')]"
            ))
        )
        buy_button.click()

        WebDriverWait(browser, Config.SEARCH_TIMEOUT).until(
            lambda d: "/afisha/city/" in d.current_url or
            "schedule" in d.current_url.lower() or
            d.find_elements(By.XPATH, "//h1[contains(., 'Расписание')]")
        )

        return movie_title

    def _select_cinema_and_session(self, browser):
        """
        Выбор кинотеатра и доступного сеанса.

        Args:
            browser: WebDriver instance

        Raises:
            AssertionError: Если не удалось найти доступные сеансы
        """
        WebDriverWait(browser, Config.ELEMENT_TIMEOUT * 3).until(
            EC.presence_of_element_located((
                By.XPATH, "//div[contains(@class, 'schedule-item')]"
            ))
        )

        self._close_popups(browser)

        cinema_items = browser.find_elements(
            By.XPATH, "//div[contains(@class, 'schedule-item')]"
        )

        selected = False
        for cinema in cinema_items:
            try:

                sessions = cinema.find_elements(
                    By.XPATH,
                    ".//span["
                    "contains(@class, 'schedule-item__session-button_active') "
                    "and not(contains(@class, 'disabled')) "
                    "and string-length(text()) > 0"
                    "]"
                )

                if sessions:
                    self._hide_interfering_elements(browser)

                    browser.execute_script(
                        "arguments[0].scrollIntoView({block: 'center'});",
                        sessions[0]
                    )
                    browser.execute_script(
                        "arguments[0].click();", sessions[0])

                    WebDriverWait(browser, 10).until(
                        lambda driver: driver.execute_script(
                            "return document.readyState"
                        ) == "complete"
                    )

                    WebDriverWait(browser, 8).until(
                        EC.presence_of_element_located((
                            By.XPATH,
                            "//iframe[contains(@src, 'afisha.yandex.ru') or "
                            "contains(@src, 'widget.afisha.yandex.ru')]"
                        ))
                    )
                    selected = True
                    break

            except Exception:
                self._restore_hidden_elements(browser)
                continue

        if not selected:
            raise AssertionError(
                "Не удалось найти кинотеатр с доступными сеансами"
            )

    def _close_popups(self, browser):
        """Закрытие всплывающих окон и модалок."""
        try:
            close_buttons = browser.find_elements(
                By.XPATH,
                "//button[contains(@class, 'close') or "
                "contains(@class, 'modal-close')]"
            )
            for btn in close_buttons:
                try:
                    btn.click()

                    WebDriverWait(browser, 1).until(
                        EC.invisibility_of_element_located((
                            By.CSS_SELECTOR,
                            ".modal-backdrop, .popup"
                        ))
                    )
                except Exception:
                    continue
        except Exception:
            pass

    def _hide_interfering_elements(self, browser):
        """Скрытие мешающих элементов."""
        try:
            iframes = browser.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    browser.execute_script(
                        "arguments[0].style.display = 'none';", iframe
                    )
                except Exception:
                    continue
        except Exception:
            pass

    def _restore_hidden_elements(self, browser):
        """Восстановление скрытых элементов."""
        try:
            iframes = browser.find_elements(By.TAG_NAME, "iframe")
            for iframe in iframes:
                try:
                    browser.execute_script(
                        "arguments[0].style.display = 'block';", iframe
                    )
                except Exception:
                    continue
        except Exception:
            pass
