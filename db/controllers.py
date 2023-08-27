import logging
from typing import List, Dict
from sqlalchemy import update, delete
from db.models import WebData, WebAnswer, DbData, DbAnswer, TempDbData, TempDbAnswer
from db.database import session
import get_webdata


def write_webdata_to_db():
    webdata = get_webdata.WebDataA()
    wd = WebData(
        user='',
        topic=webdata.get_topic_name(),
        question=webdata.get_question(),
        is_radiobutton=1 if webdata.get_selectors_type() == 'radio' else 0
    )
    WebDataController().write_data(wd)


class DataController:
    def __init__(self):
        self.model = WebData | DbData | TempDbData

    @staticmethod
    def write_data(data: DbData | DbAnswer | TempDbData | TempDbAnswer):
        session.add(data)
        session.commit()

    def read_data(self) -> List[WebData | DbData | TempDbData]:
        return session.query(self.model).all()

    def delete_data(self, id_: int):
        stmt = delete(self.model).where(self.model.id == id_)
        try:
            session.execute(stmt)
            session.commit()
        except Exception as ex:
            session.rollback()
            logging.exception(f"An error occurred during delete data from model: {self.model}")


class WebDataController(DataController):
    """Write all webdata to <webdatas> table in SQL"""

    def __init__(self):
        super().__init__()
        self.model = WebData

    def write_data(self, data: WebData):
        self.wipe_table()
        session.add(data)
        WebAnswerController().write_data(data)
        session.commit()

    @staticmethod
    def wipe_table():
        data = session.query(WebData).all()
        ids = [each.id for each in data]
        for id_num in ids:
            session.delete(session.query(WebData).filter_by(id=id_num).first())
        session.commit()


class WebAnswerController:
    @staticmethod
    def write_data(related_data: WebData):
        webdata = get_webdata.WebDataA()
        answers = webdata.get_answers()
        selected_answers = webdata.get_clicked_answers()
        correct_answers = DbDataController().read_correct_answers(question=related_data.question)
        for answer in answers:
            session.add(WebAnswer(
                text=answer,
                webdata=related_data,
                is_selected=1 if answer in selected_answers else 0,
                is_correct=1 if answer in correct_answers else 0
            ))


class DbDataController(DataController):
    """Manipulates with <dbdatas> table in SQL"""

    def __init__(self):
        super().__init__()
        self.model = DbData

    def read_correct_answers(self, question: str) -> List[str]:
        full_data = self.read_data()
        for data in full_data:
            if data.question == question:
                return [answer.text for answer in data.answers]
        return []


class DbAnswerController(DataController):
    pass


class TempDbDataController(DataController):
    def __init__(self):
        super().__init__()
        self.model = TempDbData

    @staticmethod
    def update_data(id_: int, data: Dict):
        stmt = update(TempDbData).values(data).where(TempDbData.id == id_)
        try:
            session.execute(stmt)
            session.commit()
        except Exception as ex:
            session.rollback()
            logging.exception("An error occurred during update data from model: TempDbData")


class TempDbAnswerController(DataController):
    pass
