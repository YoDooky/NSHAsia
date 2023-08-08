from dataclasses import dataclass


@dataclass
class WebData:
    """Dataclass for data from webpage"""
    user: str
    topic: str
    question: str
    answers: str
    selected_answers: str
    correct_answers: str
    is_radiobutton: int


@dataclass
class DbData:
    """Dataclass for data from db"""
    question: str
    correct_answers: str
