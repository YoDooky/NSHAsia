import time
from typing import Union

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver_init import driver


class PdfSkipper:
    def __call__(self, *args, **kwargs):
        while self.go_next_page():
            if not self.go_next_page():
                break

    @staticmethod
    def get_next_page_button() -> Union[WebElement, None]:
        next_page_mask = '//*[@class[contains(.,"icon next")]]/..'
        for i in range(3):
            driver.switch_to.window(driver.window_handles[0])
            iframe = driver.find_element(By.XPATH, '//iframe')
            driver.switch_to.frame(iframe)
            try:
                actions = ActionChains(driver)
                actions.move_by_offset(50, 50).click().perform()
                button = driver.find_element(By.XPATH, next_page_mask)
                return button
            except Exception as ex:
                time.sleep(1)
                continue

    def go_next_page(self) -> bool:
        next_button = self.get_next_page_button()
        if next_button is None:
            return False
        if next_button.get_attribute('disabled'):
            return False
        next_button.click()
        time.sleep(1)
        return True


skip_pdf = PdfSkipper()
