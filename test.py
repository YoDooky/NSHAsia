import time
from typing import Union

from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

lst_1 = ['не начат', 'в процессе', 'не пройден']
str_1 = 'awd'
if all([lst not in str_1 for lst in lst_1]):
    print('OK')
