import sys
import time
from typing import Union

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver_init import driver
from aux_functions import AuxFunc
from exceptions import TheoryNotChanges
from log import print_log
from web.xpaths import XpathResolver
from logick.aux_funcs import RandomDelay

# exception_topics = [
#     '1. Требования к персоналу, обеспечение безопасности при работе на высоте.'
# ]  # topics which theory cant be solved by standart ways


class TheoryStrategy:
    MAX_PAGE_LOAD = 10  # maximum attempts to check if page the same

    def __init__(self, topic_name: str):
        self.topic_name = topic_name
        self.same_page_counter = 0
        self.theory_click_counter = 0
        self.next_theory_button = XpathResolver.next_theory()
        self.last_page_src = None

    def skip_theory(self):
        """Skips all theory"""
        print_log('--> Прокликиваю теорию')

        # try to skip pdf if it exist
        skip_pdf = PdfSkipper()
        skip_pdf()

        # skip general theory
        while AuxFunc().try_click(xpath=self.next_theory_button, try_numb=3, window_numb=1):
            self.click_theory()
        # if self.topic_name in exception_topics:
        #     AuxFunc().try_click(
        #         xpath='//span[@id="txt4_480cf201"]',
        #         window_numb=1
        #     )  # click <ПЕРЕЙТИ К ТЕСТИРОВАНИЮ> button
        # time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver.goto_quiz_button(), try_numb=8)
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver.start_button(), try_numb=8)
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver.continue_button(), try_numb=8)

    def click_theory(self):
        current_page_src = driver.page_source
        # check if page the same
        if self.has_same_page(current_page_src=current_page_src, last_page_src=self.last_page_src):
            raise TheoryNotChanges
        self.last_page_src = current_page_src
        time.sleep(RandomDelay.get_theory_delay())
        sys.stdout.write('\r' + f"Количество успешных кликов: {self.theory_click_counter}")  # print on one line
        sys.stdout.flush()

    def has_same_page(self, current_page_src: str, last_page_src: str):
        """Checks if page src has been changed since 10 attempts"""
        if self.same_page_counter >= self.MAX_PAGE_LOAD:
            return True
        if last_page_src == current_page_src:
            self.same_page_counter += 1
        else:
            self.theory_click_counter += 1  # increase theory click counter because page has been changed
            self.same_page_counter = 0
        return False


class TheoryStrategyA(TheoryStrategy):
    """Solving theory where is standatr window"""
    pass


class TheorySolveStrategy:
    """Strategy for theory solving"""

    def __init__(self, strategy: TheoryStrategy):
        self.strategy = strategy

    def do_work(self):
        self.strategy.skip_theory()


class PdfSkipper:
    """Class for skipping pdf files"""

    def __call__(self, *args, **kwargs):
        """Skip all pdf pages"""
        print_log(message='Пробую скипнуть pdf, если он есть', silent=True)
        while self.go_next_page():
            if not self.go_next_page():
                break

    @staticmethod
    def get_next_page_button() -> Union[WebElement, None]:
        """Return next pdf page button"""
        next_page_mask = '//*[@class[contains(.,"icon next")]]/..'
        for i in range(3):
            driver.switch_to.window(driver.window_handles[-1])
            iframe = driver.find_element(By.XPATH, '//iframe')
            driver.switch_to.frame(iframe)
            try:
                actions = ActionChains(driver)
                actions.move_by_offset(0, 0).click().perform()
                button = driver.find_element(By.XPATH, next_page_mask)
                return button
            except Exception as ex:
                time.sleep(1)
                continue

    def go_next_page(self) -> bool:
        """Go next pdf page"""
        next_button = self.get_next_page_button()
        if next_button is None:
            return False
        if next_button.get_attribute('disabled'):
            return False
        next_button.click()
        time.sleep(1)
        return True
