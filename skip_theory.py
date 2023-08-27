import time
from typing import Tuple

import aux_functions


class SkipTheory:
    def __init__(self):
        self.aux_func = aux_functions.AuxFunc()
        self.next_button_mask = '//*[@class="universal-control-panel__button universal-control-panel__button_next ' \
                                'universal-control-panel__button_right-arrow"]'
        self.progress_mask = '//*[@class="progressbar__label"]'

    def __get_progress(self) -> Tuple[int, int]:
        """Returns slides progress"""
        progress_text = self.aux_func.try_get_text(xpath=self.progress_mask, amount=1, try_numb=5)
        if not progress_text:
            return 0, 0
        return int(progress_text.split(sep='/')[0].strip()), int(progress_text.split(sep='/')[1].strip())

    def skip_theory(self):
        """Skips all theory"""
        progress = self.__get_progress()
        while progress[0] < progress[1]:
            self.aux_func.try_click(xpath=self.next_button_mask)
            time.sleep(1)
            progress = self.__get_progress()
