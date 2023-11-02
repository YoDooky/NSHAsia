from aux_functions import AuxFunc
from log import init_logging_config
import config
from driver_init import driver
from logick.topic_solve import TopicSolve

if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()
    driver.get('https://pnsh.ispringlearn.ru/courses')
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
