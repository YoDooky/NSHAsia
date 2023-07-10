import sys
import time
from typing import List

from playsound import playsound
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from threading import Thread, Lock
import zipfile

from config.folders import music_path, alarm_music_path
from log import print_log

sys.tracebacklimit = 0


class AuxFunc:

    def __init__(self, driver):
        self.driver = driver

    def wait_element_load(self, xpath, timeout=10):
        """задержка для того чтобы загрузились скрипты, ajax и прочее гавно"""
        try:
            WebDriverWait(self.driver, timeout).until(ec.presence_of_element_located((By.XPATH, xpath)))
            return 1
        except TimeoutException:
            print_log(f'[ERR] Не смог дождаться загрузки элемента {xpath} в течении '
                      f'{timeout} секунд', None, None, 1)
            return 0

    def wait_window_load_and_switch(self, window_number, timeout=5):
        """функция ожидания загрузки окон и переключения на целевое окно (1й аргумент функции)"""
        try:
            self.driver.implicitly_wait(timeout)
            WebDriverWait(self.driver, timeout).until(ec.number_of_windows_to_be(window_number + 1))
            self.driver.switch_to.window(self.driver.window_handles[window_number])
            self.driver.implicitly_wait(timeout)
            return 1
        except TimeoutException:
            print_log(f'[ERR] Не смог переключиться на окно №{window_number + 1} в течении '
                      f'{timeout} секунд', None, None, 1)
            return 0

    def try_click(self, xpath, element=0, window_numb=None, try_numb=10, scroll_to=True):
        """функция для попыток клика по элементу"""
        for i in range(try_numb):
            try:
                if window_numb is not None:
                    self.driver.switch_to.window(self.driver.window_handles[window_numb])
                if scroll_to:
                    run_button_element = self.driver.find_element(By.XPATH, xpath)
                    self.driver.execute_script("arguments[0].scrollIntoView(true);", run_button_element)
                    if i % 2:
                        self.driver.execute_script("window.scrollBy(0 , 60);")
                    else:
                        self.driver.execute_script("window.scrollBy(0 , -60);")
                if element:
                    self.driver.find_elements(By.XPATH, xpath)[element].click()
                else:
                    self.driver.find_element(By.XPATH, xpath).click()
                return 1
            except Exception as ex:
                if i >= try_numb - 1:
                    print_log('[ERR] {0} Не смог кликнуть по элементу {1} в течении {2} попыток'.
                              format(ex, xpath, try_numb), None, None, 1)
                    break
                time.sleep(1)
                continue
        return 0

    def try_get_text(self, xpath, amount=0, try_numb=10) -> str | List:
        """пытаемся извлечь текст из элемента"""
        for i in range(try_numb):
            if not amount:  # если нужно искать несколько элементов
                try:
                    element = self.driver.find_elements(By.XPATH, xpath)
                except Exception as ex:
                    if i >= try_numb - 1:
                        print_log('[ERR] {0} Не смог получить текст элемента {1} в течении {2} попыток'.
                                  format(ex, xpath, try_numb), None, None, 1)
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
                                print_log('[ERR] {0} Не смог получить текст элемента {1} в течении {2} '
                                          'попыток'.format(ex, xpath, try_numb), None, None, 1)
                            time.sleep(1)
                            break
                else:  # если element пуст тогда ждем
                    time.sleep(1)
                    continue
            else:  # если нужно искать один элемент
                try:
                    element = self.driver.find_element(By.XPATH, xpath)
                except Exception as ex:
                    if i >= try_numb - 1:
                        print_log('[ERR] {0} Не смог получить текст элемента {1} в течении {2} попыток'
                                  .format(ex, xpath, try_numb), None, None, 1)
                    time.sleep(1)
                    continue
                if element:  # если element НЕ пуст. Иногда не успевает считаться значение, поэтому иначе будем ждать
                    try:
                        if element.get_attribute('innerText'):
                            return element.get_attribute('innerText')
                    except Exception as ex:
                        if i >= try_numb - 1:
                            print_log('[ERR] {0} Не смог получить текст элемента {1} в течении {2} попыток'
                                      .format(ex, xpath, try_numb), None, None, 1)
                        time.sleep(1)
                        continue
                else:  # если element пуст тогда ждем
                    time.sleep(1)
                    continue

    def try_get_id(self, xpath, try_numb=10):
        for i in range(try_numb):
            try:
                question_id = self.driver.find_elements(By.XPATH, xpath)
                return question_id
            except Exception as ex:
                if i >= try_numb - 1:
                    print_log('[ERR] {0} Не смог найти ID элемента {1} в течении {2} попыток'.
                              format(ex, xpath, try_numb), None, None, 1)
                    break
                time.sleep(1)
                continue

    def try_get_link(self, question_id, try_numb=10):
        answer_link_mask = "//*[@data-quiz-uid='" + question_id + "']//div//table//tbody//tr//td//div//span"
        for i in range(try_numb):
            try:
                question_id = self.driver.find_elements(By.XPATH, answer_link_mask)
                return question_id
            except Exception as ex:
                if i >= try_numb - 1:
                    print_log('[ERR] {0} Не смог найти ссылку на ID {1} в течении {2} попыток'.
                              format(ex, question_id, try_numb), None, None, 1)
                    break
                time.sleep(1)
                continue

    def switch_to_frame(self, xpath=None, try_numb: int = 10, windows_numb: int = 2):
        """функция для переключения на фрейм"""
        for i in range(try_numb):  # пробуем переключиться на тест
            try:
                self.driver.implicitly_wait(1)
                WebDriverWait(self.driver, 1).until(ec.number_of_windows_to_be(windows_numb))
                self.driver.switch_to.window(self.driver.window_handles[windows_numb - 1])
                self.driver.implicitly_wait(1)
                if xpath:
                    self.driver.switch_to.frame(self.driver.find_element(By.XPATH, xpath))
                else:  # если не передан путь до фрейма то берем дефолтный
                    xpath = '//*[@id="Content"]'
                    self.driver.switch_to.frame(self.driver.find_element(By.XPATH, xpath))
                break
            except Exception as ex:
                if i >= try_numb - 1:
                    print_log('[ERR] {0} Не смог перейти на фрейм {1} в течении {2} попыток'
                              .format(ex, xpath, try_numb), None, None, 1)
                time.sleep(1)
                continue


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
    print_log('Таймер кончил за {:2d} секунд!\n'.format(delay), None, None, 1)


def convert_time(time_in_sec):
    """Функция для преобразования времени из SS в MM:SS"""
    minutes = '{:02d}'.format(time_in_sec // 60)
    seconds = '{:02d}'.format(time_in_sec % 60)
    clock = minutes + ':' + seconds
    return clock


def sound_loop():
    while True:
        playsound(alarm_music_path)


def play_sound(self, alarm_type):
    if alarm_type == 1:  # если аларм не критичный (уведомление) то просто запускаем один раз звуковой файл
        playsound(music_path)
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
            # workbook = load_workbook(filename=database)
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
