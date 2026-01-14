"""
Модуль smoke-тестирования функционала покупки билетов на Кинопоиске.

Содержит end-to-end тест проверки полного цикла покупки билетов.
"""

import pytest
import allure
from config import Config
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException


@pytest.mark.smoke
@pytest.mark.ui
class TestKinopoiskTickets:
    """Тестовый класс для проверки покупки билетов на Кинопоиске."""

    @allure.feature("KR-34 / Smoke testing Kinopoisk")
    @allure.story("Подбор и покупка билетов в кино")
    def test_first_steps(self, browser):
        """End-to-end тест полного цикла покупки билетов."""
        with allure.step(
            "Step 1: Зайти на сайт Кинопоиск и перейти в раздел Билеты в кино"
        ):
            browser.get(Config.BASE_URL)
            tickets_btn = WebDriverWait(
                browser, Config.ELEMENT_TIMEOUT
            ).until(
                EC.element_to_be_clickable((
                    By.XPATH,
                    "//a["
                    "contains(@class, 'kinopoisk-header-featured-menu__item') "
                    "and contains(., 'Билеты в кино')"
                    "]"
                ))
            )
            tickets_btn.click()

        with allure.step("Step 2: Проверить/выбрать город Москва"):
            try:
                city_selector = WebDriverWait(
                    browser, Config.ELEMENT_TIMEOUT
                ).until(
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

            except Exception:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="city_selection_failed",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError("Не удалось установить город Москва")

        with allure.step(
            "Step 3: Выбрать первый фильм из списка и нажать 'Купить билеты'"
        ):
            try:
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

                first_movie.find_element(
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
                    lambda driver: "/afisha/city/" in driver.current_url or
                    "schedule" in driver.current_url.lower() or
                    driver.find_elements(
                        By.XPATH, "//h1[contains(., 'Расписание')]"
                    )
                )

            except Exception:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="film_selection_failed",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError("Не удалось выбрать первый фильм")

        with allure.step("Step 4: Выбрать кинотеатр и сеанс"):
            try:
                WebDriverWait(browser, Config.ELEMENT_TIMEOUT * 3).until(
                    EC.presence_of_element_located((
                        By.XPATH, "//div[contains(@class, 'schedule-item')]"
                    ))
                )

                try:
                    close_buttons = browser.find_elements(
                        By.XPATH,
                        "//button[contains(@class, 'close') or "
                        "contains(@class, 'modal-close')]"
                    )
                    for button in close_buttons:
                        try:
                            button.click()
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

                cinema_items = browser.find_elements(
                    By.XPATH, "//div[contains(@class, 'schedule-item')]"
                )

                selected = False
                for cinema in cinema_items:
                    try:

                        sessions = cinema.find_elements(
                            By.XPATH,
                            ".//span["
                            "contains(@class, "
                            "'schedule-item__session-button_active') "
                            "and not(contains(@class, 'disabled')) "
                            "and string-length(text()) > 0"
                            "]"
                        )

                        if sessions:
                            try:
                                iframes = browser.find_elements(
                                    By.TAG_NAME, "iframe"
                                )
                                for iframe_element in iframes:
                                    try:

                                        browser.execute_script(
                                            "arguments[0].style.display = "
                                            "'none';",
                                            iframe_element
                                        )

                                    except Exception:
                                        pass
                            except Exception:
                                pass

                            browser.execute_script(
                                "arguments[0].scrollIntoView("
                                "{block: 'center'});",
                                sessions[0]
                            )

                            browser.execute_script(
                                "arguments[0].click();", sessions[0]
                            )

                            WebDriverWait(browser, 10).until(
                                lambda driver: driver.execute_script(
                                    "return document.readyState"
                                ) == "complete"
                            )

                            try:
                                WebDriverWait(browser, 8).until(
                                    EC.presence_of_element_located((
                                        By.XPATH,
                                        "//iframe["
                                        "contains(@src, 'afisha.yandex.ru') "
                                        "or contains(@src, "
                                        "'widget.afisha.yandex.ru')"
                                        "]"
                                    ))
                                )
                                selected = True
                                break
                            except TimeoutException:
                                try:
                                    iframes = browser.find_elements(
                                        By.TAG_NAME, "iframe"
                                    )
                                    for iframe_element in iframes:
                                        try:
                                            browser.execute_script(
                                                "arguments[0].style.display = "
                                                "'block';",
                                                iframe_element
                                            )
                                        except Exception:
                                            pass
                                except Exception:
                                    pass
                                continue

                    except Exception:
                        continue

                if not selected:
                    raise Exception(
                        "Не удалось найти кинотеатр с доступными сеансами"
                    )

            except Exception:
                allure.attach(
                    browser.get_screenshot_as_png(),
                    name="session_selection_failed",
                    attachment_type=allure.attachment_type.PNG
                )
                raise AssertionError("Не удалось выбрать сеанс")
