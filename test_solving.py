# модуль для обработки данных с базы данных Excel и Web страницы теста с выводом массива элементов для клика
import time

from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import ElementClickInterceptedException

import get_excel_data
import get_webdata
import log
import main
from config import folders
import aux_functions
import make_files


def find_answer_to_click(weblist_data, database_data):
    """Функция поиска верного ответа. Если все ответы который указаны в первом стобце с ответами есть на странице
    то выбираем их. Если нет ответа или какого-нибудь из ответов на вебстранице то выбираем ответ из
    следующего столбца"""
    answer_dict = {}
    for key in weblist_data:  # переираем все значения веблисте
        if database_data.get(key):  # если есть в базе вопрос как на веблисте
            for value in database_data[key]:  # перебираем ответы из всех столбцов базы
                answer_list = clear_symbols(weblist_data[key]['answer'][0])  # вариант ответа на веблисте
                value = clear_symbols(value)
                value = value if isinstance(value, list) else [value]
                if set(value).issubset(answer_list):  # если все ответы из базы есть ответах на вопрос на странице
                    link_list = weblist_data[key]['a_link'][0]  # линки до ответов на веблисте
                    index = [answer_list.index(item) for item in value if item in answer_list]  # индексы верных ответов
                    answer_link = [link_list[each] for each in index]  # линки до верных ответов
                    question_id = weblist_data[key]['q_id'][0]
                    answer_dict[question_id] = answer_link
                    break
    return answer_dict


# функция для удаления спецсимволов из входного массива(не более чем трехмерного) или строки
def clear_symbols(string_object):
    if isinstance(string_object, list):
        each_array = []
        for each in string_object:
            every_array = []
            if isinstance(each, list):
                for every in each:
                    i_array = []
                    if isinstance(every, list):
                        for i in every:
                            i_array.append(del_specific_symbols(i))
                        every_array.append(i_array)
                    else:
                        every_array.append(del_specific_symbols(every))
                each_array.append(every_array)
            else:
                each_array.append(del_specific_symbols(each))
        clean_string = each_array
    else:
        clean_string = del_specific_symbols(string_object)
    return clean_string


# проверка на строку и удаление всех спец символов и пробелов и lowercase в строке
def del_specific_symbols(string_object):
    if isinstance(string_object, str):
        output_variable = string_object.translate(
            {ord(c): None for c in '*); \xa0'})  # игнорируем спец символы и пробелы
    else:
        output_variable = string_object
    return output_variable


def decode_data(database_data):
    """Разбиваем строку на элементы списка если есть разделитель"""
    separator = '*)'
    for each_key in database_data:
        for each_value in database_data[each_key]:
            if separator in each_value[0]:  # если есть разделитель в строке, то формируем массив
                index = database_data[each_key].index(each_value)  # индекс текущего элемента
                database_data[each_key][index] = each_value[0].split(separator)[1:]  # удаляем из массива первый
                # символ-разделитель
                
                
def convert_data(data_turple):
    """Конвертируем данные в строку по маске '*)' если передан список"""
    if len(data_turple) > 1:
        return ''.join([f'*){each};' for each in data_turple])  # преобразовываем список вопросов в строку по маске "*)"
    else:
        return data_turple[0]


def solve_test(driver, weblist_data=None, silent=0, database_data=None):
    """Кликаем по правильным ответам в тесте"""
    # aux_func = aux_functions.AuxFunc(driver)

    if not weblist_data:
        log.print_log('Пробуем решить используя ответы в базе SDO', None, None, silent)
        weblist_data = get_webdata.get_data(driver)
        data = get_excel_data.ExcelData(
            filename=file_init.database_name,
            sheetname=file_init.database_sheet)
    else:  # если массив с данными передает другая функция то выбираем другой путь до Excel (temp_base.xlxs)
        # получаем массив с данными из базы Excel
        log.print_log('Пробуем решить используя ответы во временной базе autosolve', None, None, silent)
        data = get_excel_data.ExcelData(
            filename=file_init.autosolve_database_name,
            sheetname=file_init.autosolve_database_sheet)

    # weblist_data = convert_webdata(weblist_data)
    if not database_data:
        database_data = data.get_data(start_row=2, start_column=2)  # получаем массив с данными из базы Excel
    decode_data(database_data)  # декодируем все "*)" из excel таблицы
    question_data = find_answer_to_click(weblist_data, database_data)
    # driver.maximize_window()
    click_answer(driver, question_data)


def click_answer(driver, data_dict):
    """Кликаем по ответам. 2й аргумент словарь где ключ - id, а значение - список ссылок на ответы"""
    aux_func = aux_functions.AuxFunc(driver)
    max_try = 10  # максимальное количество попыток для клика
    question_select = None  # webelement с ID вопроса
    for key in data_dict:
        for value in data_dict[key]:
            for try_numb in range(1, max_try + 1):  # пробуем кликнуть
                try:
                    aux_func.wait_element_load('//*//div//table//tbody//tr//td//div//span')
                    founded_questions_mask = f"//*[@data-quiz-uid={key}]"
                    aux_func.wait_element_load(founded_questions_mask)
                    question_select = driver.find_element(By.XPATH, founded_questions_mask)
                    driver.execute_script("arguments[0].scrollIntoView();", question_select)  # прокрутка
                    # чтобы можно было кликнуть
                    WebDriverWait(driver, main_file.driver_timeout).until(ec.visibility_of(value))  # ждем чтобы элемент
                    # был виден и кликаем по нему
                    value.click()
                    break
                except ElementClickInterceptedException:
                    question_num = question_select.get_attribute('innerText').split('\n')[1]
                    log.print_log(f'Не смог кликнуть по ответу на:\n'
                                           f'-----><{question_num}>, попытка №{try_numb}...')
                    aux_func.wait_window_load_and_switch(1)
                    aux_func.switch_to_frame(awd)
                    time.sleep(1)

                if try_numb >= max_try:
                    log.print_log(f'Не удалось кликнуть по ответу на:\n'
                                           f'-----><{question_num}> в течении {max_try} попыток')
                    log.print_log('Пробую кликнуть медленно прокручивая страницу')
                    success = False
                    window_height = driver.execute_script("return document.body.scrollHeight")  # высота HTML окна
                    for i in range(1, window_height, 50):  # медленно прокручиваем страницу
                        aux_func.wait_window_load_and_switch(1)
                        aux_func.switch_to_frame(awd)
                        driver.execute_script(f'window.scrollTo(0, {i})')
                        try:
                            value.click()
                            log.print_log('Удалось кликнуть используя медленную прокрутку')
                            success = True
                            make_files.take_screenshot(driver)
                            break
                        except ElementClickInterceptedException:
                            continue
                    if not success:
                        main_file.stop_driver(driver, 'Не смог кликнуть по элементу')


def get_unknown_question(driver=None, webdata=None, silent=True):
    """Функция для получения словаря не отвеченных вопросов"""
    if not webdata:
        webdata = get_webdata.get_data(driver)
    elif not driver and not webdata:  # вызываем exception
        raise ValueError('There is no driver object to find webdata on page faggot')
    unknown_dict = {}
    for each in webdata:
        if not sum(webdata[each]['a_checkbox'][0]):
            unknown_dict[each] = webdata[each]
    log.print_log(f'\nОстались не отвечеными {len(unknown_dict)} вопросов из {len(webdata)}. '
                           f'Это вопросы {[each for each in unknown_dict]}', None, None, silent)
    return unknown_dict
