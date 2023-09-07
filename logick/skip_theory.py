import re
import time
from typing import Tuple

from aux_functions import AuxFunc
from logick.aux_funcs import RandomDelay
from web.xpaths import XpathResolver


class TheoryStrategy:
    def __init__(self):
        self.topic_xpath = XpathResolver()

    def __get_progress(self) -> Tuple[int, int]:
        """Returns slides progress"""
        progress_text = AuxFunc().try_get_text(xpath=self.topic_xpath.theory_progress(),
                                               amount=1,
                                               try_numb=5)
        if not progress_text:
            return 0, 0
        digits = re.findall(r'\d+', progress_text)
        return int(digits[0]), int(digits[1])

    def skip_theory(self):
        """Skips all theory"""
        progress = self.__get_progress()
        while progress[0] < progress[1]:
            AuxFunc().try_click(xpath=self.topic_xpath.next_theory())
            time.sleep(RandomDelay.get_theory_delay())
            progress = self.__get_progress()
        AuxFunc().try_click(xpath=XpathResolver().start_button())


class Theory(TheoryStrategy):
    pass
