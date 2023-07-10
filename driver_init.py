from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from selenium.webdriver.chrome.options import Options
import logging
from config.folders import chromedriver_path

logging.getLogger('urllib3').setLevel('CRITICAL')
logging.getLogger('selenium').setLevel('CRITICAL')


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
        DesiredCapabilities.CHROME['goog:loggingPrefs'] = {'performance': 'ALL'}
        options = Options()
        # options.headless = True
        # options.add_experimental_option("excludeSwitches", ["enable-logging"])
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
        s = Service(chromedriver_path)
        self.browser = webdriver.Chrome(service=s, options=options)
        self.browser.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
