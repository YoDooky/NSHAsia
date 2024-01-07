from playsound import playsound
from selenium.webdriver.common.by import By

from aux_functions import AuxFunc
from config import MUSIC_FILE_PATH
from driver_init import driver


def get_topic_title():
    driver.switch_to.window(driver.window_handles[-1])
    topic_title = AuxFunc().try_get_text(xpath='//*[@id="contentItemTitle"]', amount=1)
    if topic_title in [None, '']:
        playsound(MUSIC_FILE_PATH)
        return input('Не смог найти имя темы. Скопируй имя темы вручную чтобы продолжить')
    return topic_title


driver.get('C:/Users/user/Downloads/theme_3.mhtml')
get_topic_title()
driver.quit()
driver.close()
