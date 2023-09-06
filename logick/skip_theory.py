import time
from typing import Tuple

from aux_functions import AuxFunc
from web.xpaths import XpathResolver
from web.get_webdata import WebDataA


class TheoryStrategy:
    def __init__(self):
        topic_name = WebDataA().get_topic_name()
        self.topic_xpath = XpathResolver()
        AuxFunc().switch_to_frame(xpath=self.topic_xpath.iframe())

    def __get_progress(self) -> Tuple[int, int]:
        """Returns slides progress"""
        progress_text = AuxFunc().try_get_text(xpath=self.topic_xpath.theory_progress(),
                                               amount=1,
                                               try_numb=5)
        if not progress_text:
            return 0, 0
        return int(progress_text.split(sep='/')[0].strip()), int(progress_text.split(sep='/')[1].strip())

    def skip_theory(self):
        """Skips all theory"""
        progress = self.__get_progress()
        while progress[0] < progress[1]:
            AuxFunc().try_click(xpath=self.topic_xpath.next_theory())
            # time.sleep(1)
            progress = self.__get_progress()


class Theory(TheoryStrategy):
    pass
