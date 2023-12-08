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


@dataclass
class PageType:
    """Def pages types (theory/quiz/result_page)"""
    theory = 'theory'
    quiz = 'quiz'
    result_page = 'result_page'


class UserMessages:
    """
    Class for messages to user when need to call him
    """
    input_topics_nums = ('\n-> Введи номера курсов для решения через запятую, '
                         'и/или через тире если нужно решить несколько подряд:')
    founded_next_topics = '--> В курсе найдены следующие темы:'
    cant_end_topic = '\n-> [ERR] Не могу завершить тему. Перейди на экран с темами и нажми Enter'
    cant_go_to_result_page = '\n-> [ERR] Не смог перейти на экран с результатами'
    cant_solve_topic = '-> [ERR] Не смог решить тему:'
    cant_solve_topic_try_again = '\n-> [ERR] Не смог решить тему. Пробую еще раз'
    choose_topic = '\n\n---> Выбираю тему:'
    try_solve_topic_again = '-> Пробую решить заново тему:'
    cant_fint_topic_status = '-> [ERR] Не смог найти статус (решена / не решена) для темы:'
    max_solve_attempts_exceed = ('\n-> [ERR] Превышено максимально количество попыток решения тема'
                                 '\n-> Реши сам кожаный мешок и нажми <Enter>')
