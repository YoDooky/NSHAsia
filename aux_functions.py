import logging
import sys
import time
from typing import List, Union

from playsound import playsound
from selenium.webdriver import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from threading import Thread, Lock
import zipfile

from driver_init import driver
from config.init_folders import MUSIC_FILE_PATH, ALARM_FILE_PATH
from log import print_log
import web


class AuxFunc:

    @staticmethod
    def wait_element_load(xpath, timeout=10) -> bool:
        """задержка для того чтобы загрузились скрипты, ajax и прочее гавно"""
        try:
            WebDriverWait(driver, timeout).until(ec.presence_of_element_located((By.XPATH, xpath)))
            return True
        except TimeoutException:
            print_log(f'[ERR] Не смог дождаться загрузки элемента {xpath} в течении '
                      f'{timeout} секунд', False)
            return False

    def try_click(self, xpath, element=0, window_numb=None, try_numb=10, scroll_to=True) -> bool:
        """функция для попыток клика по элементу"""
        for i in range(try_numb):
            try:
                if window_numb is not None:
                    self.switch_to_frame(web.XpathResolver.iframe())
                    # perform click
                    actions = ActionChains(driver)
                    actions.move_by_offset(0, 0).perform()
                if scroll_to:
                    run_button_element = driver.find_element(By.XPATH, xpath)
                    driver.execute_script("arguments[0].scrollIntoView(true);", run_button_element)
                    if i % 2:
                        driver.execute_script("window.scrollBy(0 , 60);")
                    else:
                        driver.execute_script("window.scrollBy(0 , -60);")
                if element:
                    driver.find_elements(By.XPATH, xpath)[element].click()
                else:
                    driver.find_element(By.XPATH, xpath).click()
                return True
            except Exception as ex:
                if i >= try_numb - 1:
                    # logging.exception(f"{ex}\nAn error occurred during trying to click")
                    break
                time.sleep(1)
                continue
        return False

    @staticmethod
    def try_webclick(element: WebElement, try_numb: int = 5):
        for i in range(try_numb):
            try:
                driver.execute_script("arguments[0].scrollIntoView(true);", element)
                element.click()
                return
            except Exception as ex:
                if i >= try_numb - 1:
                    logging.exception(f"{ex}\nAn error occurred during trying to click")
                    break
                time.sleep(1)
                continue

    @staticmethod
    def try_get_text(xpath, amount=0, try_numb=10) -> Union[str, List]:
        """пытаемся извлечь текст из элемента"""
        for i in range(try_numb):
            if not amount:  # если нужно искать несколько элементов
                try:
                    element = driver.find_elements(By.XPATH, xpath)
                except Exception as ex:
                    if i >= try_numb - 1:
                        logging.exception(f"{ex}\nAn error occurred during trying to get a bunch of text")
                    time.sleep(1)
                    continue
                text_list = []
                if element:  # если element НЕ пуст. Иногда не успевает считаться зн-ие, поэтому иначе будем ждать
                    for each in element:
                        try:
                            if each.get_attribute('innerText'):
                                text_list.append(each.get_attribute('innerText'))
                                if len(text_list) >= len(element):
                                    return text_list
                                continue
                            else:  # если хоть одно значение не содержит текст то сбрасываем счетчик найденных зн-ий
                                time.sleep(1)
                                break
                        except Exception as ex:
                            if i >= try_numb - 1:
                                logging.exception(f"{ex}\nAn error occurred during trying to get a bunch of text")
                            time.sleep(1)
                            break
                else:  # если element пуст тогда ждем
                    time.sleep(1)
                    continue
            else:  # если нужно искать один элемент
                try:
                    element = driver.find_element(By.XPATH, xpath)
                except Exception as ex:
                    if i >= try_numb - 1:
                        logging.exception(f"{ex}\nAn error occurred during trying to get a text")
                    time.sleep(1)
                    continue
                if element:  # если element НЕ пуст. Иногда не успевает считаться значение, поэтому иначе будем ждать
                    try:
                        if element.get_attribute('innerText'):
                            return element.get_attribute('innerText')
                    except Exception as ex:
                        if i >= try_numb - 1:
                            logging.exception(f"{ex}\nAn error occurred during trying to get a text")
                        time.sleep(1)
                        continue
                else:  # если element пуст тогда ждем
                    time.sleep(1)
                    continue

    @staticmethod
    def try_get_attribute(xpath: str, attribute: str, try_numb: int = 5) -> str:
        """Return target attribute of web element"""
        for i in range(try_numb):
            try:
                element = driver.find_element(By.XPATH, xpath).get_attribute(attribute)
                return element
            except Exception:
                time.sleep(1)
                continue
        logging.exception("An error occurred during trying to get an attribute of text")

    @staticmethod
    def switch_to_frame(xpath=None, try_numb: int = 10) -> bool:
        """функция для переключения на фрейм"""
        for i in range(try_numb):  # пробуем переключиться на тест
            try:
                driver.implicitly_wait(1)
                # WebDriverWait(self.driver, 1).until(ec.number_of_windows_to_be(windows_numb))
                # driver.switch_to.window(driver.window_handles[windows_numb - 1])
                driver.switch_to.window(driver.window_handles[-1])
                driver.implicitly_wait(1)
                if xpath:
                    driver.switch_to.frame(driver.find_element(By.XPATH, xpath))
                return True
            except Exception as ex:
                if i >= try_numb - 1:
                    logging.exception(f"{ex}\nAn error occurred during trying to switch to iframe")
                time.sleep(1)
                continue
        return False

    def random_delay_timer(self, timer_multiply, lock=Lock()):
        """Задержка с отображением оставшегося времени"""
        delay = timer_multiply
        for remaining in range(delay, 0, -1):
            lock.acquire()
            sys.stdout.write("\r")
            rem_time = self.convert_time(remaining)
            del_time = self.convert_time(delay)
            sys.stdout.write("{:s} ({:2d} секунд) осталось из {:s} ({:2d} секунд)."
                             .format(rem_time, remaining, del_time, delay))
            sys.stdout.flush()
            lock.release()
            time.sleep(1)
        sys.stdout.write("\rТаймер кончил за {:2d} секунд!            \n".format(delay))
        print_log('Таймер кончил за {:2d} секунд!\n'.format(delay), False)

    @staticmethod
    def convert_time(time_in_sec):
        """Функция для преобразования времени из SS в MM:SS"""
        minutes = '{:02d}'.format(time_in_sec // 60)
        seconds = '{:02d}'.format(time_in_sec % 60)
        clock = minutes + ':' + seconds
        return clock

    @staticmethod
    def sound_loop():
        while True:
            playsound(ALARM_FILE_PATH)

    def play_sound(self, alarm_type: int = 1):
        if alarm_type == 1:  # если аларм не критичный (уведомление) то просто запускаем один раз звуковой файл
            playsound(MUSIC_FILE_PATH)
        elif alarm_type == 10:  # если аларм критичный то запускаем аларм в цикле в потоке
            thread = Thread(target=self.sound_loop)
            thread.start()

    def wait_for_user(self, err_message):
        """ожидание ввода пользователя"""
        print_log(err_message)
        self.play_sound(1)
        accept = input()
        if accept == 'x':
            sys.exit()
        elif accept == 'z':
            return 2
        else:
            return 1


def database_permission(workbook, database, try_numb=100):
    for i in range(1, try_numb + 1):
        try:
            # workbook = load_workbook(filename=db)
            workbook.save(database)
            break
        except PermissionError:
            print_log(f'Нет доступа к файлу: <{database}> для записи. Попытка №{i + 1}...')
            time.sleep(1)
        except zipfile.BadZipFile:
            print_log(f'Нет доступа к файлу: <{database}> для записи. Попытка №{i + 1}...')
            time.sleep(1)
        if i >= try_numb:
            print_log(f'Не смогу получить доступа к файлу: <{database}> '
                      f'для записи в течении {try_numb} попыток')
            print_log('[ALARM] Не получилось записать в базу. ВЫХОЖУ ИЗ ПРОГИ!')
            sys.exit()
