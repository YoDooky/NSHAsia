from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
import logging
from selenium.webdriver.remote.remote_connection import LOGGER

from config.folders import CHROMEDRIVER_PATH

LOGGER.setLevel(logging.WARNING)
logging.getLogger("urllib3").setLevel(logging.WARNING)
logging.getLogger("selenium").setLevel(logging.WARNING)


class BrowserDriver:
    __instance = None

    def __new__(cls, *args, **kwargs):
        if cls.__instance is None:
            cls.__instance = super().__new__(cls)
            cls._set_options(cls.__instance)
        return cls.__instance

    def __del__(self):
        BrowserDriver.__instance = None

    def _set_options(self):
        options = Options()
        options.add_argument('--log-level=3')
        options.add_argument("start-maximized")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_argument("incognito")
        options.add_experimental_option('useAutomationExtension', False)
        options.add_argument("--disable-blink-features")
        options.add_argument("--disable-blink-features=AutomationControlled")
        # # options.add_argument('--headless')
        # # options.add_argument('--disable-gpu')
        options.add_argument("--disable-infobars")
        options.add_argument("--disable-extensions")
        options.add_experimental_option("prefs", {
            "profile.default_content_setting_values.notifications": 1
        })
        s = Service(CHROMEDRIVER_PATH)
        self.browser = webdriver.Chrome(service=s, options=options)
        self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
