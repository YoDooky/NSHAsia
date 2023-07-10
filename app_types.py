from dataclasses import dataclass


@dataclass
class WebData:
    """Dataclass for data from webpage"""
    user: str
    question: str
    question_num: int
    question_id: int
    answer: str
    answer_checkbox: str
    is_radiobutton: int
