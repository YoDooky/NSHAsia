from sqlalchemy import Column, String, Integer, ForeignKey
from sqlalchemy.orm import declarative_base, relationship

Base = declarative_base()


class WebData(Base):
    __tablename__ = 'webdatas'

    id = Column('id', Integer, primary_key=True)
    user = Column('user', String)
    topic = Column('topic', String)
    question = Column('question', String)
    is_radiobutton = Column('is_radiobutton', Integer)
    answers = relationship('WebAnswer', back_populates='webdata',
                           cascade='all, delete-orphan')  # last option to delete related table

    def __init__(self, user: str, topic: str, question: str, is_radiobutton: int = 0):
        self.user = user
        self.topic = topic
        self.question = question
        self.is_radiobutton = is_radiobutton


class WebAnswer(Base):
    __tablename__ = 'webanswers'

    id = Column('id', Integer, primary_key=True)
    text = Column('text', String)
    is_selected = Column('is_selected', Integer)

    webdata_id = Column(Integer, ForeignKey(f'{WebData.__tablename__}.id'))
    webdata = relationship(WebData.__name__, back_populates='answers')

    def __init__(self, text: str, webdata: WebData, is_selected: int = 0):
        self.text = text
        self.webdata = webdata
        self.is_selected = is_selected


class DbData(Base):
    __tablename__ = 'dbdatas'

    id = Column('id', Integer, primary_key=True)
    topic = Column('topic', String)
    question = Column('question', String)

    answers = relationship('DbAnswer', back_populates='dbdata',
                           cascade='all, delete-orphan')  # last option to delete related table

    def __init__(self, question: str, topic: str):
        self.topic = topic
        self.question = question


class DbAnswer(Base):
    __tablename__ = 'dbanswers'

    id = Column('id', Integer, primary_key=True)
    text = Column('text', String)
    is_correct = Column('is_correct', Integer)

    dbdata_id = Column(Integer, ForeignKey(f'{DbData.__tablename__}.id'))
    dbdata = relationship(DbData.__name__, back_populates='answers')

    def __init__(self, text: str, dbdata: DbData, is_correct: int = 0):
        self.text = text
        self.dbdata = dbdata
        self.is_correct = is_correct


class TempDbData(Base):
    __tablename__ = 'tempdbdatas'

    id = Column('id', Integer, primary_key=True)
    topic = Column('topic', String)
    question = Column('question', String)
    last_answer_combination = Column('last_answer_combination', Integer)
    current_answer_combination = Column('current_answer_combination', Integer)

    answers = relationship('TempDbAnswer', back_populates='tempdbdata',
                           cascade='all, delete-orphan')  # last option to delete related table

    def __init__(self, question: str, topic: str, last_answer_combination: int | None = None,
                 current_answer_combination: int | None = None):
        self.topic = topic
        self.question = question
        self.last_answer_combination = last_answer_combination
        self.current_answer_combination = current_answer_combination


class TempDbAnswer(Base):
    __tablename__ = 'tempdbanswers'

    id = Column('id', Integer, primary_key=True)
    text = Column('text', String)

    tempdbdata_id = Column(Integer, ForeignKey(f'{TempDbData.__tablename__}.id'))
    tempdbdata = relationship(TempDbData.__name__, back_populates='answers')

    def __init__(self, text: str, tempdbdata: TempDbData):
        self.text = text
        self.tempdbdata = tempdbdata


class Xpath(Base):
    __tablename__ = 'xpaths'
    id = Column('id', Integer, primary_key=True)
    topic = Column('topic', String)
    xpath = Column('xpath', String)
    element = Column('element', String)

    def __init__(self, topic: str, xpath: str, element: str):
        self.topic = topic
        self.xpath = xpath
        self.element = element
