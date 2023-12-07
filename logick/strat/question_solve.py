import re
import time
from typing import Union, Type, List
from playsound import playsound
from selenium.webdriver.remote.webelement import WebElement

from config import MUSIC_FILE_PATH
from db import (
    write_webdata_to_db,
    DbDataController,
    DbAnswerController,
    WebDataController,
    TempDbDataController,
    DbData,
    DbAnswer,
    WebData,
    TempDbData
)
from exceptions import NoSelectedAnswer, NoAnswerResult
from logick.strat.utils import RandomDelay
from web.xpaths import XpathResolver
from aux_functions import AuxFunc
from web.xpaths import TopicWebData
from log import print_log
from logick.strat.utils import GenerateVariant, CalculateVariants


def validate_db_data(main_data: Union[WebData, DbData, TempDbData],
                     comp_data: Union[WebData, DbData, TempDbData]) -> bool:
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
            return [TopicWebData().get_link(answer) for answer in next_answers]
        first_answer = GenerateVariant().generate(web_data[0])
        print_log(f'--> Вопроса нет в базах: \n {web_data[0].question}'
                  f'\n-> Выбираю от пизды (нет) ответ: \n {first_answer}')
        return [TopicWebData().get_link(first_answer)]

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
            return [TopicWebData().get_link(answer) for answer in right_answers]
        return self.get_answers_from_temp_db()


class QuestionStrategy:
    def __init__(self):
        pass

    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()

        if not self.choose_answer(links):
            return

        write_webdata_to_db()  # update data to write selected answers
        AuxFunc().try_click(xpath=XpathResolver.answer_button())  # click <ОТВЕТИТЬ> button

        if self.is_correct_answer():
            self.write_if_correct_result()
        else:
            self.write_if_wrong_result()

    @staticmethod
    def choose_answer(links: List[WebElement]) -> bool:
        for link in links:
            time.sleep(RandomDelay.get_question_delay())
            if not AuxFunc.try_webclick(link):
                playsound(MUSIC_FILE_PATH)
                print_log('[ERR]Не удалось кликнуть по ответу')
                input('Выбери ответ, нажми <Ответить> (если есть) и для продолжения нажми Enter...')
                return False
        return True

    def is_correct_answer(self) -> bool:
        answer_result = AuxFunc().try_get_text(
            xpath=XpathResolver.answer_result(),
            amount=1,
            try_numb=2
        ).lower().replace(' ', '')
        if answer_result is None:
            raise NoAnswerResult
        if 'неправильно' in answer_result:
            return False
        elif 'правильно' in answer_result:
            return True
        raise NoAnswerResult

    @staticmethod
    def write_if_wrong_result():
        """Update answer combination in temp db"""
        print_log('x  Ответ неверный')
        web_data = WebDataController().read()
        temp_data = TempDbDataController().read()
        for temp in temp_data:
            if not validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().update(id_=temp.id,
                                          data={'last_answer_combination': temp.current_answer_combination})

    def write_if_correct_result(self):
        """Writes corrects data to db and delete it from temp db"""
        print_log('v  Ответ правильный')

        web_data = WebDataController().read()

        if self.validate_data(web_data):  # if there is same question don't write to db
            return

        if 1 not in [answer.is_selected for answer in
                     web_data[0].answers]:  # check if there is selected answer in web data
            raise NoSelectedAnswer

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
    def validate_data(web_data) -> bool:
        """Check for same data in db with correct answers"""
        db_data = DbDataController().read()
        for db in db_data:
            if not validate_db_data(main_data=db, comp_data=web_data[0]):
                continue
            return True
        return False


class QuestionStrategyA(QuestionStrategy):
    """Question strategy for topics where the result (правильно/неправильно) of question solve is exist"""
    pass


class QuestionStrategyB(QuestionStrategy):
    """Question strategy for topics where the result (правильно/неправильно) of question solve doesn't exist
    and topic score (набрано балов X из X) is existed"""

    def __init__(self):
        super().__init__()
        self.start_score = None

    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()
        self.start_score = self.get_result_data()  # trying to get current topic result (if it exists)

        if not self.choose_answer(links):
            return

        write_webdata_to_db()  # update data to write selected answers
        AuxFunc().try_click(xpath=XpathResolver.answer_button())  # click <ОТВЕТИТЬ> button

        result = self.is_correct_answer()
        if result is None:
            return
        if result:
            self.write_if_correct_result()
        else:
            self.write_if_wrong_result()

    @staticmethod
    def get_result_data() -> Union[int, None]:
        """Returns current topic score"""
        mask = XpathResolver.current_score()
        topic_score_text = AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2)  # ЗДЕСЬ ЛУЧШЕ ПОМЕНЯТЬ СТРАТЕГИЮ
        if topic_score_text is None:
            return None
        return int(re.findall(r'\d+', topic_score_text)[0])

    def is_correct_answer(self) -> Union[bool, None]:
        if self.start_score is None:
            raise NoAnswerResult
        current_score = self.get_result_data()
        if current_score is None:
            return
        if self.start_score < current_score:
            return True
        return False


class QuestionSolveStrategy:
    """Strategy for solving questions"""

    def __init__(self, strategy: Type[QuestionStrategy]):
        self.strategy = strategy

    def do_work(self):
        return self.strategy().solve_question()
