import logging
from typing import List, Dict, Union
from sqlalchemy import update, delete
from db.models import WebData, WebAnswer, DbData, DbAnswer, TempDbData, TempDbAnswer, Xpath, User
from db.database import session
import web  # import WebDataA


def write_webdata_to_db():
    webdata = web.TopicWebData()
    wd = WebData(
        user='',
        topic=webdata.get_topic_name(),
        question=webdata.get_question(),
        is_radiobutton=1 if webdata.get_selectors_type() == 'radio' else 0
    )
    WebDataController().write(wd)


class DataController:
    def __init__(self):
        self.model = Union[WebData, WebAnswer, DbData, DbAnswer, TempDbData, TempDbAnswer, Xpath, User]

    @staticmethod
    def write(data: Union[WebData, WebAnswer, DbData, DbAnswer, TempDbData, TempDbAnswer, Xpath, User]):
        session.add(data)
        session.commit()

    def read(self) -> List[Union[WebData, WebAnswer, DbData, DbAnswer, TempDbData, TempDbAnswer, Xpath, User]]:
        return session.query(self.model).all()

    def update(self, id_: int, data: Dict):
        stmt = update(self.model).values(data).where(self.model.id == id_)
        try:
            session.execute(stmt)
            session.commit()
        except Exception as ex:
            session.rollback()
            logging.exception(f"[ERR]\n    {ex}\nAn error occurred during update data from model: {self.model}")

    def delete(self, id_: int):
        stmt = delete(self.model).where(self.model.id == id_)
        try:
            session.execute(stmt)
            session.commit()
        except Exception as ex:
            session.rollback()
            logging.exception(f"[ERR]\n    {ex}\nAn error occurred during delete data from model: {self.model}")

    def clear_table(self):
        data = session.query(self.model).all()
        ids = [each.id for each in data]
        for id_num in ids:
            session.delete(session.query(self.model).filter_by(id=id_num).first())
        session.commit()


class WebDataController(DataController):
    """Write all webdata to <webdatas> table in SQL"""

    def __init__(self):
        super().__init__()
        self.model = WebData

    def write(self, data: WebData):
        self.clear_table()
        session.add(data)
        WebAnswerController().write_data(data)
        session.commit()


class WebAnswerController:
    @staticmethod
    def write_data(related_data: WebData):
        webdata = web.TopicWebData()
        answers = webdata.get_answers()
        selected_answers = webdata.get_clicked_answers()
        for answer in answers:
            session.add(WebAnswer(
                text=answer,
                webdata=related_data,
                is_selected=1 if answer in selected_answers else 0
            ))


class DbDataController(DataController):
    """Manipulates with <dbdatas> table in SQL"""

    def __init__(self):
        super().__init__()
        self.model = DbData

    def read_correct_answers(self, question: str) -> List[str]:
        full_data = self.read()
        for data in full_data:
            if data.question == question:
                return [answer.text for answer in data.answers]
        return []


class DbAnswerController(DataController):
    def __init__(self):
        super().__init__()
        self.model = DbAnswer


class TempDbDataController(DataController):
    def __init__(self):
        super().__init__()
        self.model = TempDbData


class TempDbAnswerController(DataController):
    def __init__(self):
        super().__init__()
        self.model = TempDbAnswer


class XpathController(DataController):
    def __init__(self):
        super().__init__()
        self.model = Xpath


class UserController(DataController):
    def __init__(self):
        super().__init__()
        self.model = User
