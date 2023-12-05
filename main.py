from playsound import playsound

from config import MUSIC_FILE_PATH
from db import UserController
from log import init_logging_config, print_log
import config
from driver_init import driver
from db.sql_to_excel import excel_data
from logick.solve.course_solve import CourseSolve


if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()

    playsound(MUSIC_FILE_PATH)
    if input('\nНажми <y>, посчитай до 3 секунд, после нажми Enter для выгрузки в excel'
             '\nЕсли не хочешь выгружать просто нажми Enter'
             '\nЕсли нихуя не понял просто нажми Enter') == 'y':
        excel_data.export_to_excel()

    driver.get('https://pnsh.ispringlearn.ru/courses')

    print('<<<<<    15.11.2023. NSHAsia rev.0.0.8  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        playsound(MUSIC_FILE_PATH)
        repeat = input('\nНажми <Enter> чтобы решить курс уважаемый человек (петушок).')
        UserController().clear_table()
        try:
            driver.switch_to.window(driver.window_handles[0])
            CourseSolve().main()
        except Exception as ex:
            print_log(message='[ERR] Возникла проблема при решении всего курса', exception=ex)
        playsound(MUSIC_FILE_PATH)

    driver.quit()
    driver.close()
