from typing import Type, Union

from selenium.webdriver.remote.webelement import WebElement
from typing import List

from db import DbDataController, WebDataController, TempDbDataController, \
    WebData, DbData, TempDbData
from logick import GenerateVariant, CalculateVariants, strat

from web.xpaths import WebDataA
from log import print_log


def validate_db_data(main_data: WebData | DbData | TempDbData, comp_data: WebData | DbData | TempDbData) -> bool:
    """Checks if there is same data in both data"""
    # compare question text
    if main_data.question != comp_data.question:
        return False
    # compare answers amount
    if len(main_data.answers) != len(comp_data.answers):
        return False
    # compare answers text
    comp_data_answers = [answer.text for answer in comp_data.answers]
    for answer in main_data.answers:
        if answer.text not in comp_data_answers:
            return False

    return True


class AnswerChoice:
    @staticmethod
    def get_answers_from_temp_db() -> List[WebElement]:
        """Returns answer from TempDbData. If no data in TempDbData then returns first answer"""
        web_data = WebDataController().read()
        temp_data = TempDbDataController().read()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            next_answers = CalculateVariants().get_next_variants(data=temp,
                                                                 prev_variant_num=temp.last_answer_combination)
            print_log(f'--> Вопрос найден во временной базе: \n {temp.question}'
                      f'\n-> Выбираю ответы на вопрос из временной базы: \n {next_answers}')
            return [WebDataA().get_link(answer) for answer in next_answers]
        first_answer = GenerateVariant().generate(web_data[0])
        print_log(f'--> Вопроса нет в базах: \n {web_data[0].question}'
                  f'\n-> Выбираю от пизды (нет) ответ: \n {first_answer}')
        return [WebDataA().get_link(first_answer)]

    @staticmethod
    def get_db_right_answers(db_data: List[DbData]) -> List[str]:
        web_data = WebDataController().read()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            return [answer.text for answer in db.answers if answer.is_correct]

    def get_right_answers_links(self) -> List[WebElement]:
        """Returns answer from DbData. If no data in DbData then returns next answer from TempDbData"""
        db_data = DbDataController().read()
        web_data = WebDataController().read()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            right_answers = self.get_db_right_answers(db_data)
            print_log(f'--> Вопрос найден в базе: \n {db.question}'
                      f'\n-> Выбираю ответы на вопрос из базы: \n '
                      f'{[answer.text for answer in db.answers if answer.is_correct]}')
            return [WebDataA().get_link(answer) for answer in right_answers]
        return self.get_answers_from_temp_db()


class QuestionSolve:
    def __init__(self, strategy: Union[Type[strat.QuestionStrategy], None]):
        self.strategy = strategy

    def solve_question(self) -> Type[strat.QuestionStrategy]:
        if self.strategy is None:
            self.define_strategy()
        strat.QuestionSolveStrategy(self.strategy).do_work()
        return self.strategy

    def define_strategy(self):
        """Find demand question solve strategy for current topic depending on founded xpath (current_score)"""
        try:
            if strat.QuestionStrategyB().get_result_data() is None:
                self.strategy = strat.QuestionStrategyA
            self.strategy = strat.QuestionStrategyB
        except IndexError:
            self.strategy = strat.QuestionStrategyA
