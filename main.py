import sys

from selenium.webdriver.common.by import By

import aux_functions
import get_webdata
from config.folders import init_folders
import driver_init


def main():
    init_folders()
    driver = driver_init.BrowserDriver().browser
    aux_func = aux_functions.AuxFunc(driver)

    driver.get('E:/Downloads/NSH_templates/type_1/init_state.mhtml')
    xpath = '//*[@class="content_frame"]'
    aux_func.switch_to_frame(xpath=xpath, windows_numb=1)
    wb = get_webdata.WebDataA()
    answers = wb.get_answer()
    link = wb.get_link(answers[1])
    print('')


if __name__ == '__main__':
    print('<<<<<    21.06.2023. NSHAsia rev.0.0.1  >>>>>')  # version description
    main()

