import aux_functions
import solve.main
from db.controllers import WebDataController
from config.folders import init_folders
import driver_init
import skip_theory


def main():
    init_folders()

    driver = driver_init.BrowserDriver().browser
    aux_func = aux_functions.AuxFunc()

    # driver.get('E:/Downloads/NSH_templates/type_1/init_state.mhtml')
    driver.get('https://pnsh.ispringlearn.ru/')

    input('Жми')
    aux_func.switch_to_frame(xpath='//*[@class="content_frame"]')

    skip_theory.SkipTheory().skip_theory()
    WebDataController().write_data()

    while True:
        solve.main.solve_question()

    print('')
    driver.quit()
    driver.close()


if __name__ == '__main__':
    print('<<<<<    21.06.2023. NSHAsia rev.0.0.1  >>>>>')  # version description
    main()
