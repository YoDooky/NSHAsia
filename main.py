from log import init_logging_config
from config.folders import Folders
import driver_init
from logick.topic_solve import TopicSolve

if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    Folders.init_folders()
    driver_init.BrowserDriver().browser.get('https://pnsh.ispringlearn.ru/courses')

    print('<<<<<    25.08.2023. NSHAsia rev.0.0.2  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        repeat = input('Нажми <Enter> чтобы решить следующую тему петушок. Нажми <q> для выхода')
        if repeat == 'q':
            break
        TopicSolve().main()

    driver_init.BrowserDriver().browser.quit()
    driver_init.BrowserDriver().browser.close()
