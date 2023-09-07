import itertools
from random import randint
from typing import List

from config.read_config import read_config_file
from db.controllers import TempDbDataController, TempDbAnswerController
from db.models import WebData, TempDbData, TempDbAnswer
from exceptions import MaxVariantsExceeded


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
        prev_variant_num = self.validate_number(num=prev_variant_num, max_num=len(combinations) - 1)
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
    def validate_number(num: int, max_num: int):
        if num is None:
            return 0
        if num <= 0:
            return 0
        if num >= max_num:
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
