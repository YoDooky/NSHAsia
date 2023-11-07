from aux_functions import AuxFunc
from log import init_logging_config
import config
from driver_init import driver
from logick.topic_solve import TopicSolve
from db.sql_to_excel import excel_data

if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()
    excel_data.export_to_excel()
    # driver.get('https://pnsh.ispringlearn.ru/courses')
    # driver.get('https://ucpermoil.ispringlearn.ru/courses')
    # driver.get('C:/Users/user/Downloads/tests/Подготовительные работы.html')

    print('<<<<<    20.10.2023. NSHAsia rev.0.0.5  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        repeat = input('Нажми <Enter> чтобы решить следующую тему петушок.')
        if repeat == 'q':
            break
        TopicSolve().main()
        AuxFunc().play_sound()

    driver.quit()
    driver.close()
