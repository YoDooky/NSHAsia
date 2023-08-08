from typing import List

from db.models import WebData, WebAnswer, DbData, DbAnswer
from db.database import session
import get_webdata


class WebDataController:
    """Write all webdata to <webdatas> table in SQL"""

    def write_data(self):
        self.wipe_table()

        webdata = get_webdata.WebDataA()
        wd = WebData(
            user='',
            topic=webdata.get_topic_name(),
            question=webdata.get_question(),
            is_radiobutton=1 if webdata.get_selectors_type() == 'radio' else 0
        )
        session.add(wd)
        WebAnswerController().write_data(wd)
        session.commit()

    @staticmethod
    def read_data() -> List[WebData]:
        return session.query(WebData).all()

    @staticmethod
    def wipe_table():
        data = session.query(WebData).all()
        ids = [each.id for each in data]
        for id_num in ids:
            session.delete(session.query(WebData).filter_by(id=id_num).first())
        session.commit()


class WebAnswerController:
    @staticmethod
    def write_data(related_webdata: WebData):
        webdata = get_webdata.WebDataA()
        answers = webdata.get_answers()
        selected_answers = webdata.get_clicked_answers()
        correct_answers = DbDataController().read_correct_answers(question=related_webdata.question)
        for answer in answers:
            session.add(WebAnswer(
                text=answer,
                webdata=related_webdata,
                is_selected=1 if answer in selected_answers else 0,
                is_correct=1 if answer in correct_answers else 0
            ))


class DbDataController:
    """Manipulates with <dbdatas> table in SQL"""

    @staticmethod
    def write_data():
        session.add(DbData(question='q1', correct_answers='a2'))
        session.commit()

    @staticmethod
    def read_data() -> List[DbData]:
        return session.query(DbData).all()

    def read_correct_answers(self, question: str) -> List[str]:
        full_data = self.read_data()
        for data in full_data:
            if data.question == question:
                return [answer.text for answer in data.answers]
        return []
