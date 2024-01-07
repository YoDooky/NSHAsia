from playsound import playsound

from app_types import UserMessages, TopicData, ProgramMode
from aux_functions import AuxFunc
from config import MUSIC_FILE_PATH
from db import UserController
from exceptions import QuizEnded
from log import init_logging_config, print_log
import config
from driver_init import driver
from db.sql_to_excel import excel_data
from logick.solve.course_solve import CourseSolve
from logick.solve.topic_solve import TopicSolve


def import_db():
    """
    Asks do you need to import data from sqlite to excel
    :return:
    """
    playsound(MUSIC_FILE_PATH)
    if input('\nНажми <y>, посчитай до 3 секунд, после нажми Enter для выгрузки в excel'
             '\nЕсли не хочешь выгружать просто нажми Enter'
             '\nЕсли нихуя не понял просто нажми Enter') == 'y':
        excel_data.export_to_excel()


def get_topic_title() -> str:
    """
    Returns topic title if user select topic solve mode
    :return: Topic title
    """
    driver.switch_to.window(driver.window_handles[-1])
    topic_title = AuxFunc().try_get_text(xpath='//*[@id="contentItemTitle"]', amount=1)
    if topic_title in [None, '']:
        playsound(MUSIC_FILE_PATH)
        return input('Не смог найти имя темы. Скопируй имя темы вручную чтобы продолжить')
    return topic_title


def solve_selected_program_mode(user_input: str):
    """
    Solve whole course/topic depends on program mode
    :param user_input: user input (program mode)
    :return:
    """
    if user_input == ProgramMode.course_solve:
        try:
            CourseSolve().main()
        except QuizEnded:
            print_log('КАЛ РЕШЕН!')
        except Exception as ex:
            print_log(message=UserMessages.err_while_solve_whole, exception=ex)
    elif user_input == ProgramMode.topic_solve:
        try:
            TopicSolve().main(TopicData(name=get_topic_title()))
        except QuizEnded:
            print_log('КАЛ РЕШЕН!')
        except Exception as ex:
            print_log(message=UserMessages.err_while_solve_whole, exception=ex)
    else:
        print('ТЫ ВТИРАЕШЬ КАКУЮ-ТО ДИЧЬ. Попробуй еще раз...')
        user_input = input(UserMessages.choose_program_mode)
        solve_selected_program_mode(user_input)


if __name__ == '__main__':
    print('<<<<<    12.12.2023. NSHAsia rev.0.0.9  >>>>>')  # version description
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()
    import_db()
    driver.get('https://pnsh.ispringlearn.ru/courses')
    repeat = ''
    while repeat != 'quit':
        playsound(MUSIC_FILE_PATH)
        repeat = input(UserMessages.choose_program_mode)
        UserController().clear_table()
        driver.switch_to.window(driver.window_handles[0])
        solve_selected_program_mode(repeat)
        playsound(MUSIC_FILE_PATH)

    driver.quit()
    driver.close()
