import re
from typing import Union

from exceptions import NoAnswerResult

from db import DbDataController, DbAnswerController, WebDataController, TempDbDataController, write_webdata_to_db, \
    DbData, DbAnswer
from exceptions import NoSelectedAnswer
from logick import question_solve, click_answer
from web.xpaths import XpathResolver
from aux_functions import AuxFunc
from log import print_log


class QuestionStrategy:
    def __init__(self):
        pass

    def solve_question(self):
        write_webdata_to_db()
        links = question_solve.AnswerChoice().get_right_answers_links()

        click_answer(links)
        write_webdata_to_db()  # update data to write selected answers
        AuxFunc().try_click(xpath=XpathResolver().answer_button())  # click <ОТВЕТИТЬ> button

        if self.find_result():
            self.write_if_correct_result()
        else:
            self.write_if_wrong_result()

    @staticmethod
    def get_result_data() -> str:
        return AuxFunc().try_get_text(xpath=XpathResolver().answer_result(), amount=1, try_numb=2)

    def find_result(self) -> bool:
        answer_result = self.get_result_data().lower().replace(' ', '')
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
            if not question_solve.validate_db_data(main_data=temp, comp_data=web_data[0]):
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
            if not question_solve.validate_db_data(main_data=temp, comp_data=web_data[0]):
                continue
            TempDbDataController().delete(temp.id)

    @staticmethod
    def validate_data(web_data) -> bool:
        """Check for same data in db with correct answers"""
        db_data = DbDataController().read()
        for db in db_data:
            if not question_solve.validate_db_data(main_data=db, comp_data=web_data[0]):
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
        links = question_solve.AnswerChoice().get_right_answers_links()
        self.start_score = self.get_result_data()  # trying to get current topic result (if it exists)

        click_answer(links)
        write_webdata_to_db()  # update data to write selected answers
        AuxFunc().try_click(xpath=XpathResolver().answer_button())  # click <ОТВЕТИТЬ> button

        result = self.find_result()
        if result is None:
            return
        if result:
            self.write_if_correct_result()
        else:
            self.write_if_wrong_result()

    @staticmethod
    def get_result_data() -> Union[int, None]:
        """Returns current topic score"""
        mask = XpathResolver().current_score()
        topic_score_text = AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2)  # ЗДЕСЬ ЛУЧШЕ ПОМЕНЯТЬ СТРАТЕГИЮ
        if topic_score_text is None:
            return None
        return int(re.findall(r'\d+', topic_score_text)[0])

    def find_result(self) -> Union[bool, None]:
        if self.start_score is None:
            raise NoAnswerResult
        current_score = self.get_result_data()
        if current_score is None:
            return
        if self.start_score < current_score:
            return True
        return False

# class QuestionStrategyC(QuestionStrategyB):
#     """Question strategy for topics where the result (правильно/неправильно) of question solve doesn't exist
#     and topic score (набрано балов X из X) is existed and last question result is not existed"""
