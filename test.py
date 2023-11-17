from selenium.webdriver.common.by import By

from log import print_log, init_logging_config
from driver_init import driver

init_logging_config()

lst_1 = [1, 2]
try:
    # print(lst_1[5])
    driver.find_element(By.XPATH, 'awdawdawdawd')
except Exception as ex:
    print_log(message='ERR', exception=ex)
    driver.quit()
driver.quit()
