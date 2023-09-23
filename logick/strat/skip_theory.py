import time

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By

import driver_init
from aux_functions import AuxFunc
from web.xpaths import XpathResolver
from logick.aux_funcs import RandomDelay


class TheoryStrategy:

    @staticmethod
    def skip_theory():
        """Skips all theory"""
        driver = driver_init.BrowserDriver().browser
        next_theory_button = XpathResolver().next_theory()
        while True:
            try:
                driver.find_element(By.XPATH, next_theory_button)
                time.sleep(RandomDelay.get_theory_delay())
                actions = ActionChains(driver)
                actions.move_by_offset(0, 0).click().perform()
                AuxFunc().try_click(xpath=next_theory_button)
            except Exception:
                break
        AuxFunc().try_click(xpath=XpathResolver().start_button(), try_numb=3)


class TheoryA(TheoryStrategy):
    """Solving theory in tests where theory progress is exist"""
    pass

#
# class TheoryB(TheoryStrategy):
#     """Solving theory in tests where theory progress doesn't exist
#     Solves theory while button next_theory is existed"""
#     pass
