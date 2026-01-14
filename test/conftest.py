"""
Конфигурация тестов с использованием pytest и Selenium WebDriver.

Содержит фикстуры для управления браузером в автоматизированных тестах.
"""

import pytest
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service as ChromeService
from webdriver_manager.chrome import ChromeDriverManager


@pytest.fixture(scope="function")
def browser():
    """
    Фикстура для инициализации и управления браузером Chrome в тестах.

    Эта фикстура выполняет следующие действия:
    - Создает экземпляр браузера Chrome с настройками анти-детекта
    - Максимизирует окно браузера перед началом теста
    - Автоматически устанавливает совместимую версию ChromeDriver
    - Гарантирует закрытие браузера после завершения теста

    Scope: function - создается новый браузер для каждого теста

    Yields:
        WebDriver: Объект драйвера Selenium WebDriver для управления браузером

    Example:
        def test_example(browser):
            browser.get("https://example.com")
            assert "Example" in browser.title
    """
    chrome_options = Options()

    # Базовые настройки
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--disable-webgl")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-gpu")

    # Настройки для обхода детекции автоматизации
    chrome_options.add_argument(
        "--disable-blink-features=AutomationControlled")
    chrome_options.add_experimental_option(
        "excludeSwitches", ["enable-automation", "enable-logging"]
    )
    chrome_options.add_experimental_option("useAutomationExtension", False)

    # Дополнительные настройки для маскировки
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--profile-directory=Default")
    chrome_options.add_argument("--ignore-certificate-errors")
    chrome_options.add_argument("--disable-plugins-discovery")
    chrome_options.add_argument("--incognito")

    # Настройки пользовательского агента
    chrome_options.add_argument(
        "--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )

    # Отключение сохранения паролей и уведомлений
    chrome_options.add_experimental_option("prefs", {
        "profile.default_content_setting_values.notifications": 2,
        "credentials_enable_service": False,
        "profile.password_manager_enabled": False,
        "profile.default_content_settings.popups": 0,
        "download.default_directory": "/tmp",
        "directory_upgrade": True,
        "safebrowsing.enabled": True
    })

    # Инициализация драйвера
    driver = webdriver.Chrome(
        service=ChromeService(ChromeDriverManager().install()),
        options=chrome_options
    )

    # JavaScript-инъекция для скрытия автоматизации
    scripts = [
        "Object.defineProperty(navigator, 'webdriver',{get: () => undefined})",
        "window.navigator.chrome = {runtime: {}, app: {},};",
        "Object.defineProperty(navigator, 'languages', "
        "{get: () => ['ru-RU', 'ru', 'en-US', 'en']});",
        "Object.defineProperty(navigator, 'plugins', "
        "{get: () => [1, 2, 3, 4, 5]});",
        "Object.defineProperty(navigator, 'hardwareConcurrency', "
        "{get: () => 8});"
    ]

    for script in scripts:
        try:
            driver.execute_script(script)
        except Exception:
            continue

    # CDP команды для обхода детекции
    driver.execute_cdp_cmd("Network.setUserAgentOverride", {
        "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    })

    driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
        "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            });
            Object.defineProperty(navigator, 'languages', {
                get: () => ['ru-RU', 'ru', 'en-US', 'en']
            });
        """
    })

    yield driver
    driver.quit()


@pytest.fixture(scope="function")
def browser_with_delay():
    """
    Фикстура браузера с добавлением случайных задержек между действиями.

    Для имитации человеческого поведения.
    """
    import random
    import time

    driver = browser()

    # Переопределяем методы для добавления задержек
    original_get = driver.get

    def delayed_get(url):
        # Случайная задержка перед переходом
        time.sleep(random.uniform(2.0, 5.0))
        return original_get(url)

    driver.get = delayed_get

    yield driver
    driver.quit()
