from selenium.webdriver.common.by import By

from driver_init import driver
from log import print_log

try:
    driver.find_element(By.XPATH, '//ddddawd23434343443/dawdwdadwa').click()
except Exception as ex:
    print_log(f'{ex} Возникла ошибка')
