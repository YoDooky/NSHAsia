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


class UserMessages:
    """
    Class for messages to user when need to call him
    """
    cant_end_topic = '\n-> [ERR] Не могу завершить тему. Перейди на экран с темами и нажми Enter'
    cant_go_to_result_page = '\n-> [ERR] Не смог перейти на экран с результатами'
