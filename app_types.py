from dataclasses import dataclass

from selenium.webdriver.remote.webelement import WebElement


@dataclass
class FormField:
    """Form(анкета) data class"""
    input_name: str
    input_link: WebElement


@dataclass
class TopicData:
    """Topic data class"""
    name: str
    status: str
    type: str = ''
    link: WebElement = None


class TopicType:
    page = 'Страница'
    study_material = 'Учебный материал'
    video = 'Видео'
