import re
import time
from selenium.webdriver import ActionChains
import logging

from log import print_log, init_logging_config
from config.folders import Folders
import aux_functions
from aux_functions import AuxFunc
from solve.main import QuestionSolve
import driver_init
import skip_theory


def click_next_button(mask: str):
    """Click button"""
    AuxFunc().switch_to_frame(xpath='//*[@class="content_frame"]')
    driver = driver_init.BrowserDriver().browser
    actions = ActionChains(driver)
    try_numb = 5
    for i in range(try_numb):
        actions.move_by_offset(0, 0).click().perform()
        if not AuxFunc().try_click(xpath=mask, scroll_to=False, try_numb=2):
            continue
        else:
            return True
    return False


def get_topic_score():
    mask = '//*[@class="player-shape-view"]'
    text = AuxFunc().try_get_text(xpath=mask)
    if int(text[-1].split('%')[0].strip()) >= int(text[-3].split('%')[0].strip()):
        return True
    return False


def get_questions_left() -> int:
    mask = '//*[@class="quiz-top-panel__question-score-info quiz-top-panel__question-score-info_with-separator"]'
    text = AuxFunc().try_get_text(xpath=mask, amount=1)
    number_list = [int(number) for number in re.findall(r'\d+', text)]
    return number_list[-1] - number_list[0]


def reboot_question_page() -> None:
    """Reboot question page"""
    driver = driver_init.BrowserDriver().browser
    driver.refresh()
    driver.switch_to.alert.accept()
    aux_functions.AuxFunc().switch_to_frame(xpath='//iframe[@class="content_frame"]')
    aux_functions.AuxFunc().try_click(xpath='//button[@class="message-box-buttons-panel__window-button"]')


def wait_next_question(last_questions_left) -> bool:
    """Wait next question load"""
    for x in range(20):
        if last_questions_left == get_questions_left():
            time.sleep(1)
        else:
            return True
    return False


def solve_question(num: int):
    """Solve current question"""
    if num != 0:
        last_questions_left = get_questions_left()
        click_next_button(
            mask=f'//button[@class="quiz-control-panel__button quiz-control-panel__button_right-arrow '
                 f'quiz-control-panel__button_show-arrow"]//*[contains(text(),"ПРОДОЛЖИТЬ")]')
        if not wait_next_question(last_questions_left):
            reboot_question_page()
    QuestionSolve().solve_question()


def solve_topic() -> bool:
    """Solve current topic"""
    try:
        AuxFunc().switch_to_frame(xpath='//*[@class="content_frame"]')
        questions_left = get_questions_left()
        for i in range(questions_left + 1):
            solve_question(i)
        click_next_button(
            mask='//*[@class="quiz-control-panel__container quiz-control-panel__container_right"]//'
                 'button[@class="quiz-control-panel__button"]//*[contains(text(),"СМОТРЕТЬ РЕЗУЛЬТАТЫ")]')
        if get_topic_score():
            return True
        click_next_button('//*[@class="player-shape-view player-shape-view_button"]')
        solve_topic()
    except Exception as ex:
        print_log(f'Ошибка: {ex}. Возникла проблема при решении курса. Пробую еще раз')
        logging.exception("An error occurred during topic solving")
        reboot_question_page()
        solve_topic()
    print_log('Решение темы завершено')


def main():
    input('Перейди на экран с выбранной темой и нажми <Enter>')
    AuxFunc().switch_to_frame(xpath='//*[@class="content_frame"]')
    skip_theory.SkipTheory().skip_theory()
    solve_topic()


if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    Folders.init_folders()
    driver_init.BrowserDriver().browser.get('https://pnsh.ispringlearn.ru/courses')

    print('<<<<<    25.08.2023. NSHAsia rev.0.0.2  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        repeat = input('Нажми <Enter> чтобы решить следующую тему петушок. Нажми <q> для выхода')
        main()

    driver_init.BrowserDriver().browser.quit()
    driver_init.BrowserDriver().browser.close()
