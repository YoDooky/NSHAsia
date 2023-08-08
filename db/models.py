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
    is_correct = Column('is_correct', Integer)

    webdata_id = Column(Integer, ForeignKey(f'{WebData.__tablename__}.id'))
    webdata = relationship(WebData.__name__, back_populates='answers')

    def __init__(self, text: str, webdata: WebData, is_selected: int = 0, is_correct: int = 0):
        self.text = text
        self.webdata = webdata
        self.is_selected = is_selected
        self.is_correct = is_correct


class DbData(Base):
    __tablename__ = 'dbdatas'

    id = Column('id', Integer, primary_key=True)
    question = Column('question', String)

    answers = relationship('DbAnswer', back_populates='dbdata',
                           cascade='all, delete-orphan')  # last option to delete related table

    def __init__(self, question: str):
        self.question = question


class DbAnswer(Base):
    __tablename__ = 'dbanswers'

    id = Column('id', Integer, primary_key=True)
    text = Column('text', String)

    dbdata_id = Column(Integer, ForeignKey(f'{DbData.__tablename__}.id'))
    dbdata = relationship(DbData.__name__, back_populates='answers')

    def __init__(self, text: str, dbdata: DbData):
        self.text = text
        self.dbdata = dbdata
