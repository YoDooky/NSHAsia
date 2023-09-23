import re
from exceptions import NoAnswerResult

from db import DbDataController, DbAnswerController, WebDataController, TempDbDataController, write_webdata_to_db, \
    DbData, DbAnswer
from logick import click_answer
from logick.question_solve import AnswerChoice, validate_db_data
from web.xpaths import XpathResolver
from aux_functions import AuxFunc
from log import print_log


class QuestionStrategy:

    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()

        # start_score = ResultStrategyB().get_result_text()  # trying to get current topic result (if it exists)
        click_answer(links)
        AuxFunc().try_click(xpath=XpathResolver().answer_button())  # click <ОТВЕТИТЬ> button

        if self.find_result():
            self.write_if_correct_result()
        self.write_if_wrong_result()

    @staticmethod
    def get_result_data():
        return AuxFunc().try_get_text(xpath=XpathResolver().answer_result(), amount=1, try_numb=2)

    def find_result(self):
        answer_result = self.get_result_data().lower().replace(' ', '')
        if 'неправильно' in answer_result:
            return False
        elif 'правильно' in answer_result:
            return True
        raise NoAnswerResult

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


class QuestionStrategyA(QuestionStrategy):
    """Question strategy for topics where the result (правильно/неправильно) of question solve is exist"""
    pass


class QuestionStrategyB(QuestionStrategy):
    """Question strategy for topics where the result (правильно/неправильно) of question solve doesn't exist
    and topic score (набрано балов X из X) is existed"""

    def __init__(self):
        self.start_score = None

    def solve_question(self):
        write_webdata_to_db()
        links = AnswerChoice().get_right_answers_links()

        self.start_score = self.get_result_data()  # trying to get current topic result (if it exists)
        click_answer(links)
        AuxFunc().try_click(xpath=XpathResolver().answer_button())  # click <ОТВЕТИТЬ> button

        if self.find_result():
            self.write_if_correct_result()
        self.write_if_wrong_result()

    @staticmethod
    def get_result_data():
        """Returns current topic score"""
        mask = XpathResolver().current_score()
        topic_score_text = AuxFunc().try_get_text(xpath=mask, amount=1, try_numb=2)
        return int(re.findall(r'\d+', topic_score_text)[0])

    def find_result(self):
        if self.start_score is None:
            raise NoAnswerResult
        if self.start_score < self.get_result_data():
            return True
        return False
