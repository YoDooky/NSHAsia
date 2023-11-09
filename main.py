from playsound import playsound

from config import MUSIC_FILE_PATH
from db import UserController
from log import init_logging_config
import config
from driver_init import driver
from db.sql_to_excel import excel_data
from logick.solve.course_solve import CourseSolve


# noinspection GrazieInspection
if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()
    excel_data.export_to_excel()
    driver.get('https://pnsh.ispringlearn.ru/courses')
    # driver.get('https://ucpermoil.ispringlearn.ru/courses')
    # driver.get('C:/Users/user/Downloads/tests/Подготовительные работы.html')

    print('<<<<<    08.11.2023. NSHAsia rev.0.0.8  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        playsound(MUSIC_FILE_PATH)
        repeat = input('\nНажми <Enter> чтобы решить следующий курс уважаемый человек (петушок).')
        if repeat == 'q':
            break
        UserController().clear_table()
        CourseSolve().main()
        playsound(MUSIC_FILE_PATH)

    driver.quit()
    driver.close()
