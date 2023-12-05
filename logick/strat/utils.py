import itertools
import time
from random import randint
from typing import List

from selenium.common import NoAlertPresentException

from aux_functions import AuxFunc
from config.read_config import read_config_file
from db import TempDbDataController, TempDbAnswerController, WebData, TempDbData, TempDbAnswer
from driver_init import driver
from exceptions import MaxVariantsExceeded, NoFoundedElement
from web import XpathResolver


class RandomDelay:
    @staticmethod
    def get_question_delay():
        """Returns randomly 0.5 to 1 parts of delay from config file"""
        delay = int(read_config_file()['answer_delay'])
        return randint(int(delay / 2), delay)

    @staticmethod
    def get_theory_delay():
        """Returns randomly 0.5 to 1 parts of delay from config file"""
        delay = int(read_config_file()['theory_delay'])
        return randint(int(delay / 2), delay)


class CalculateVariants:

    def get_next_variants(self, data: TempDbData, prev_variant_num: int) -> List[str]:
        """Returns next answers combinations and write answer combination to db"""
        answers = [answer.text for answer in data.answers]
        amount = len(answers)
        combinations = self.get_possible_combinations(amount)
        prev_variant_num = self.validate_number(num=prev_variant_num, max_num=len(combinations) - 1, data_id=data.id)
        TempDbDataController().update(id_=data.id, data={
            'current_answer_combination': prev_variant_num + 1})  # write current variant to db
        return [answers[num - 1] for num in combinations[prev_variant_num + 1]]

    @staticmethod
    def get_possible_combinations(amount: int) -> List[tuple]:
        """Return all possible combination for current <amount> of variants"""
        variant_list = []
        for i in range(1, amount + 1):
            variant_list.append([each for each in itertools.combinations([i for i in range(1, amount + 1)], i)])
        combinations = []
        for variant in variant_list:
            for each in variant:
                if len(each) == 1:
                    combinations.append(each)
                    continue
                combinations.append(each)
        return combinations

    @staticmethod
    def validate_number(num: int, max_num: int, data_id: int):
        if num is None:
            return 0
        if num <= 0:
            return 0
        if num >= max_num:
            TempDbDataController().delete(id_=data_id)  # write current variant to db
            raise MaxVariantsExceeded
        return num


class GenerateVariant:

    @staticmethod
    def generate(webdata: WebData) -> str:
        """Writes new question and answers to temp db and returns first answer variant"""
        temp_data = TempDbData(question=webdata.question, topic=webdata.topic, current_answer_combination=0)
        TempDbDataController.write(temp_data)
        for answer in webdata.answers:
            TempDbAnswerController.write(TempDbAnswer(text=answer.text, tempdbdata=temp_data))
        return webdata.answers[0].text


def set_popup(approve: bool = True):
    """
    Intercepts pop-up window which asks to continue quiz
    :param approve: if True then it will choose <Да> button (means repeat quiz from last stage)
    :return: None
    """
    AuxFunc().switch_to_frame(xpath=XpathResolver.iframe())
    if approve:
        AuxFunc().try_click(xpath=XpathResolver.popup_approve(), try_numb=3)
    else:
        AuxFunc().try_click(xpath=XpathResolver.popup_disagree(), try_numb=3)
    time.sleep(3)


def close_alert():
    """
    CLoses browser alert window
    :return:
    """
    time.sleep(1)
    try:
        driver.switch_to.alert.accept()
    except NoAlertPresentException:
        return


def is_quiz() -> bool:
    """
    Check if there is quiz question
    :return: True if there is quiz on page
    """
    try:
        question_text = AuxFunc().try_get_text(
            xpath=XpathResolver.question_text(),
            try_numb=5
        )
        answer_text = AuxFunc().try_get_text(
            xpath=XpathResolver.answer_text(),
            try_numb=5
        )
    except NoFoundedElement:
        return False
    if question_text is None or answer_text is None:
        return False
    if len(question_text) > 1:
        return False
    return True
