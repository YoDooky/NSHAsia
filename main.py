import log
from log import init_logging_config
import config
import driver_init
from logick.topic_solve import TopicSolve

if __name__ == '__main__':
    init_logging_config()  # initiate logging config
    config.Folders.init_folders()
    driver_init.BrowserDriver().browser.get('https://pnsh.ispringlearn.ru/courses')
    # driver_init.BrowserDriver().browser.get('https://ucpermoil.ispringlearn.ru/courses')
    # driver_init.BrowserDriver().browser.get('C:/Users/user/Downloads/tests/Подготовительные работы.html')

    print('<<<<<    20.10.2023. NSHAsia rev.0.0.5  >>>>>')  # version description

    repeat = ''
    while repeat != 'q':
        repeat = input('Нажми <Enter> чтобы решить следующую тему петушок.')
        if repeat == 'q':
            break
        TopicSolve().main()

    driver_init.BrowserDriver().browser.quit()
    driver_init.BrowserDriver().browser.close()
