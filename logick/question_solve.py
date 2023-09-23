# import re
from typing import Union

from selenium.webdriver.remote.webelement import WebElement
from typing import List

# from app_types import Strategies
from db import DbDataController, DbAnswerController, WebDataController, TempDbDataController, write_webdata_to_db, \
    WebData, DbData, DbAnswer, TempDbData
from logick import GenerateVariant, CalculateVariants, click_answer
from logick.strat.find_answer_result import ResultStrategyA, ResultStrategyB
from logick.strat.strategy import AnswerResultStrategy
from web.xpaths import WebDataA, XpathResolver
from aux_functions import AuxFunc
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
    # def __init__(self, strategies: Strategies):
    #     self.topic_xpath = XpathResolver()
    #     self.strategies = strategies
    def __init__(self):
        self.topic_xpath = XpathResolver()

    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()

        start_score = ResultStrategyB().get_result_text()  # trying to get current topic result (if it exists)
        click_answer(links)
        AuxFunc().try_click(xpath=self.topic_xpath.answer_button())  # click <ОТВЕТИТЬ> button

        if self.get_result(start_score):
            self.write_if_correct_result()
        self.write_if_wrong_result()

    def get_result(self, start_score: Union[int, None]):
        """Returns question solve result"""
        if start_score is None:
            # self.strategies = Strategies(
            #     question_solve_result=ResultStrategyA(),
            #     theory_skip=None
            # )
            return AnswerResultStrategy(ResultStrategyA()).do_work()
        # self.strategies = Strategies(
        #     question_solve_result=ResultStrategyB,
        #     theory_skip=None
        # )
        return AnswerResultStrategy(ResultStrategyB()).do_work()

    @staticmethod
    def write_if_wrong_result():
        """Update answer combination in temp db"""
        print_log('X  Ответ неверный')
        web_data = WebDataController().read()
        temp_data = TempDbDataController().read()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().update(id_=temp.id,
                                          data={'last_answer_combination': temp.current_answer_combination})

    def write_if_correct_result(self):
        """Writes corrects data to db and delete it from temp db"""
        print_log('✔  Ответ правильный')
        write_webdata_to_db()  # update data to write selected answers
        web_data = WebDataController().read()
        if self.validate_data(web_data):  # if there is same question don't write to db
            return
        db_data = DbData(question=web_data[0].question, topic=web_data[0].topic)
        DbDataController.write(db_data)
        for answer in web_data[0].answers:
            DbAnswerController.write(DbAnswer(text=answer.text,
                                              dbdata=db_data,
                                              is_correct=1 if answer.is_selected else 0))
        self.clear_tempdb_question(web_data)

    @staticmethod
    def clear_tempdb_question(web_data):
        """Check for same data in temp db and delete it"""
        temp_data = TempDbDataController().read()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().delete(temp.id)

    @staticmethod
    def validate_data(web_data):
        """Check for same data in db with correct answers"""
        db_data = DbDataController().read()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            return True
        return False
