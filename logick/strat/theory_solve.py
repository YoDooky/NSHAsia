import sys
import time

from driver_init import driver
from aux_functions import AuxFunc
from exceptions import TheoryNotChanges
from log import print_log
from web.xpaths import XpathResolver
from logick.aux_funcs import RandomDelay


class TheoryStrategy:
    MAX_PAGE_LOAD = 10  # maximum attempts to check if page the same

    def __init__(self):
        self.same_page_counter = 0
        self.theory_click_counter = 0
        self.next_theory_button = XpathResolver().next_theory()

    def skip_theory(self):
        """Skips all theory"""
        print_log('--> Прокликиваю теорию')
        last_page_src = None
        while AuxFunc().try_click(xpath=self.next_theory_button, try_numb=3, window_numb=1):
            # check if page the same
            current_page_src = driver.page_source
            if self.has_same_page(current_page_src=current_page_src, last_page_src=last_page_src):
                raise TheoryNotChanges
            last_page_src = current_page_src

            time.sleep(RandomDelay.get_theory_delay())
            sys.stdout.write('\r' + f"Количество успешных кликов: {self.theory_click_counter}")  # print on one line
            sys.stdout.flush()
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver().start_button(), try_numb=8)
        time.sleep(5)
        AuxFunc().try_click(xpath=XpathResolver().continue_button(), try_numb=8)

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


class TheoryA(TheoryStrategy):
    """Solving theory in tests where theory progress is exist"""
    pass

#
# class TheoryB(TheoryStrategy):
#     """Solving theory in tests where theory progress doesn't exist
#     Solves theory while button next_theory is existed"""
#     pass
