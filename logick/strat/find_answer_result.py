import re

from exceptions import NoAnswerResult
from web.xpaths import XpathResolver
from aux_functions import AuxFunc


class ResultStrategy:

    def get_result_text(self):
        return AuxFunc().try_get_text(xpath=XpathResolver().answer_result(), amount=1, try_numb=2)

    def find_result(self):
        answer_result = self.get_result_text().lower().replace(' ', '')
        if 'неправильно' in answer_result:
            return False
        elif 'правильно' in answer_result:
            return True
        raise NoAnswerResult


class ResultStrategyA(ResultStrategy):
    """Finding question result when there is a pop-up window with result(Правильно/Неправильно)"""
    pass


class ResultStrategyB(ResultStrategy):
    """Finding question result when there is a current topic score"""
    LAST_SCORE = None

    @classmethod
    def get_result_text(cls):
        """Returns current topic score"""
        mask = XpathResolver().current_score()
        topic_score_text = AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2)
        cls.LAST_SCORE = int(re.findall(r'\d+', topic_score_text)[0])
        return cls.LAST_SCORE

    def find_result(self):
        if self.LAST_SCORE is None:
            raise NoAnswerResult
        if self.LAST_SCORE < self.get_result_text():
            return True
        return False
