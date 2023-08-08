import re
from selenium.webdriver.common.by import By
from selenium.common.exceptions import NoAlertPresentException
import aux_functions
import main
import log
import random
import time
import config.read_config


def get_section(driver):
    """Поиск номера текущего раздела"""
    section_mask = '//div[@class="section-title-area"]//div[@class="before-title"]'  # маска для определения № раздела
    aux_func = aux_functions.AuxFunc()
    section_text = aux_func.try_get_text(section_mask, amount=1)
    try:
        current_section = int(re.findall(r'\d+', section_text)[0])
    except Exception as ex:
        prog_logging.print_log(f'Ошибка: {ex}. Не могу получить web element с номером раздела')
        current_section = 0
    return current_section  # получаем номер текущего раздела


def get_leftsection(driver):
    """Поиск количества оставшихся разделов"""
    section_mask = '//div[@class="section-title-area"]//div[@class="before-title"]'  # маска для определения № раздела
    if len(driver.find_elements(By.XPATH, section_mask)) > 1:  # если на одной странице больше одного раздела,
        # то значит все разделы на одной странице
        return 1
    aux_func = aux_functions.AuxFunc(driver)
    section_text = aux_func.try_get_text(section_mask, amount=1)
    try:
        section_left = int(re.findall(r'\d+', section_text)[1]) - \
                       int(re.findall(r'\d+', section_text)[0]) + 1  # выясняем количество оставшихся разделов
    except Exception as ex:
        prog_logging.print_log(f'Ошибка: {ex}. Не могу посчитать оставшееся кол-во разделов. Считаю что остался один')
        section_left = 1
    return section_left  # получаем количество оставшихся разделов


def get_startbutton(test_type='prvt'):
    """XPath для кнопки *Начать*"""
    start_button_mask = 0
    if test_type == 'prvt':
        start_button_mask = '//*[@class="mira-horizontal-layout-wrapper clearfix"]//' \
                            '*[@class="button mira-button-primary mira-button"]'
    elif test_type == 'simple':
        start_button_mask = '//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[7]//button'
    return start_button_mask


def get_answerbutton():
    """Получаем путь до кнопки 'Ответить'"""
    answer_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                         'check_button quiz_models_components_button_check_button")]]'  # кнопка Ответить
    return answer_button_mask


def get_prevbutton():
    """Получаем путь до кнопки 'Назад'"""
    prev_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                       'prev_button quiz_models_components_button_prev_button")]]'
    # prev_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
    #                    'prev_button quiz_models_components_button_prev_button")]]//*[text()="Назад"]'
    return prev_button_mask


def get_nextbutton():
    """Получаем путь до кнопки 'Далее'"""
    next_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                       'next_button quiz_models_components_button_next_button")]]//*[text()="Далее"]'
    return next_button_mask


def get_beginbutton() -> str:
    """Получаем путь до кнопки 'начать' перед запуском ПРВТ"""
    begin_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button ' \
                        'destroyable next_button quiz_models_components_button_next_button")]]//*' \
                        '[text()="Начать"]'
    return begin_button_mask


def get_information_button() -> str:
    """Получаем путь до кнопки 'Сведения'"""
    information_button_mask = "//*[@class='mira-tabs-toc-group-caption' and text()=' Сведения']"
    return information_button_mask


def get_endtest_button() -> str:
    endtest_button_mask = '//*[@class[contains(.,"ui-button ui-corner-all quiz_components_button_button destroyable ' \
                          'next_button quiz_models_components_button_next_button")]]'  # кнопка Завершить тестирование
    return endtest_button_mask


def get_progress(driver, selected_score, test_number) -> str:
    """Функция для нахождения процента сдачи. Если % сдачи < выбранного юзером % сдачи то тест сдается и возвращает 1"""
    progress_mask = '//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[5]//div//' \
                    'div//div//*[@class="mira-progress-label-progress-value"]'
    test_status_mask = '//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[4]'
    aux_func = aux_functions.AuxFunc(driver)
    aux_func.wait_element_load(progress_mask)
    try:
        progress_value = driver.find_elements(By.XPATH, progress_mask)[test_number].get_attribute('innerText')  # получ
        # аем значение процента сдачи с символом %
        test_status = driver.find_elements(By.XPATH, test_status_mask)[test_number].get_attribute('innerText')  # получ
        # аем статус теста (завершен/в процессе и т.п.)
        progress_value = int(re.findall(r'\d+', progress_value)[0])  # находим значение процента сдачи
    except Exception as ex:
        prog_logging.print_log('{0} На вебстранице не указан процент сдачи. Буду сдавать принудительно'.format(ex))
        return 'undone'
    if progress_value < selected_score:
        return 'undone'
    elif 'В процессе' in test_status:
        return 'unfinished'
    else:
        return 'complete'


def get_result(driver):
    """Функция для нахождения результата тестирования на финальном экране"""
    result_mask = '//*[@class="section-area-content"]//*[contains(text(),"Результат в процентах")]'  # элемент с
    # процентом сдачи
    aux_func = aux_functions.AuxFunc(driver)
    result_text = aux_func.try_get_text(result_mask, amount=1)
    result_score = int(re.findall(r'\d+', result_text)[0])
    return result_score


def get_questionsamount(driver):
    """Функция для определения количества вопросов в во всем тесте"""
    amount_of_questions_mask = '//*[@class="for-padding"]//*[@class="info"]'
    aux_func = aux_functions.AuxFunc(driver)
    try:
        amount_of_questions_text = aux_func.try_get_text(amount_of_questions_mask, amount=1)
    except Exception as ex:
        prog_logging.print_log(f'Ошибка <{ex}>. Не смог посчитать общее число вопросов')
        return 0
    amount_of_questions = int(re.findall(r'\d+', amount_of_questions_text)[1])
    return amount_of_questions


def get_sectionamount(driver):
    """Функция для определения общего количества разделов в тесте (в оглавлении)"""
    amount_of_questions_mask = '//*[@class="for-padding"]//*[@class="info"]'
    aux_func = aux_functions.AuxFunc(driver)
    try:
        amount_of_sections = aux_func.try_get_text(amount_of_questions_mask, amount=1)
    except Exception as ex:
        prog_logging.print_log(f'Ошибка <{ex}>. Не смог посчитать общее число разделов')
        return 0
    amount_of_sections = int(re.findall(r'\d+', amount_of_sections)[0])
    return amount_of_sections


def get_delay(driver, questions_amount):
    """Функция для выбора временной задержки в конце модуля"""
    delay_factor_min = float(config.read_config.main()['section_delay_min'])  # мин. коэффициент для задержки завершения
    delay_factor_max = float(config.read_config.main()['section_delay_max'])  # макс. коэффициент для задержки заверш.
    test_timer_mask = '//*[@class="timer-value quiz_main_text_timer destroyable"]'
    aux_func = aux_functions.AuxFunc(driver)
    test_timer_val = aux_func.try_get_text(test_timer_mask, amount=1)  # оставшееся время на тест (в формате MM:SS)
    if test_timer_val:
        test_timer_sec = int(test_timer_val.rsplit(':')[0].strip()) * 60 + int(
            test_timer_val.rsplit(':')[1].strip())  # конвертируем формат из MM:SS в секунды
        timer_delay = random.randint(int(test_timer_sec * delay_factor_min), int(test_timer_sec * delay_factor_max))
        prog_logging.print_log('Программа нашла в тесте таймер. Считаем задержку исходя из таймера на сайте\n'
                               f'Задержка равна: {aux_func.convert_time(timer_delay)}')
        return timer_delay
    else:  # если в тесте нет таймера то считаем исходя из количества вопросов
        random_question_delay = random.randint(questions_amount * 24, questions_amount * 29)
        prog_logging.print_log('Программа НЕ нашла в тесте таймер. Считаем задержку исходя из количества вопросов\n'
                               f'Задержка равна: {aux_func.convert_time(random_question_delay)}')
        return random_question_delay  # если прога не нашла таймер, то задержка равна random_question_delay


def get_tests_amount(driver, course_url, course_name, test_type):
    """Функция для нахождения количества тестов в теме (матрёшка ЁПТ)"""
    run_test_button_mask = ['//*[@class="tree-node tree-node-type-testcontentsection"]//ancestor::tr[1]//td[7]',
                            '//*[@class="mira-horizontal-layout-wrapper clearfix"]//*'
                            '[@class="button mira-button-primary mira-button"]']  # маска для поиска кнопки запуска
    # не ПРВТ и ПРВТ тестирования соответственно. В итоговом тесте кнопка появлятся после прохождения предъидущих
    aux_func = aux_functions.AuxFunc(driver)
    aux_func.wait_window_load_and_switch(0)
    driver.get(course_url)  # Переход на страницу с выбранным тестом
    driver.get(course_url)  # Сука тупорылый сайт не переходит по url с первого раза
    aux_func.try_click(get_information_button(), 0, 0)  # на всякий случай
    # кликаем "Сведения"
    aux_func.wait_window_load_and_switch(0)
    if aux_func.wait_element_load('//*[@class="path-state-name mira-bread_crumbs-object" '
                                  'and contains(text(),"ПРВТ: Сводный")]', 5):
        return 1  # выходим из функции так как у ПРВТ 1 тест в теме
    tests_counter = 0  # Счетчик не найденных кнопок с запуском теста
    if test_type == 1:  # если это ПРВТ или Excel
        tests_counter = 1
    else:
        for i in range(10):
            try:
                aux_func.wait_element_load(run_test_button_mask[0])
                tests_counter += len(driver.find_elements(By.XPATH, run_test_button_mask[0]))  # считаем кол-во тестов
                # в теме
                if tests_counter > 0:
                    break
            except Exception as ex:
                time.sleep(1)
                continue
    prog_logging.print_log(f'<{course_name}> В курсе всего {tests_counter} тестов')
    return tests_counter


def get_resultpage(driver, finish_section=0, repeat=3):
    """Функция для перехода на окно с результатами тестирования"""
    aux_func = aux_functions.AuxFunc(driver)

    def repeat_action(xpath, frame=None):
        """Повтор фокусировки и клика. В случае неудачи перезагрузка и повтор"""
        try_numb = 5
        for i in range(try_numb):
            aux_func.wait_window_load_and_switch(1)
            aux_func.switch_to_frame() if not frame else aux_func.switch_to_frame(frame, 2)
            aux_func.wait_element_load(xpath, 2)
            if aux_func.try_click(xpath, 0, None, 2):
                return
            else:
                prog_logging.print_log(f'Не могу кликнуть по <{xpath}>\n'
                                       f'-->Пробую перефокусироваться и еще раз кликнуть')
                time.sleep(1)
        if repeat > 0:  # если передано число поторов перезагрузки функции
            prog_logging.print_log(f'Не смог перефокусироваться и кликнуть по <{xpath}> в течении {try_numb} попыток\n'
                                   f'-->Пробую перезагрузить страницу и снова перефокусироваться и кликнуть...')
            driver.refresh()
            aux_func.try_click(get_prevbutton())  # кликаем кнопку 'Назад'
            get_resultpage(driver, finish_section, repeat - 1)
            if not repeat:  # если число повторов исчерпалось
                main_file.stop_driver(driver, f'Не удалось использовать баг фиксика. Закрываю тестирование')

    if finish_section:
        # кликаем "Ответить"
        prog_logging.print_log('Юзаем баг фиксика...')
        repeat_action(get_answerbutton())
    # кликаем "Выйти"
    repeat_action('//*[@class="blockmenu_link" and text()="Выйти"]', '//*[@id="LMSController"]')
    # закрываем окно с предупреждением
    try:
        driver.switch_to.alert.accept()
    except NoAlertPresentException:
        pass
    # кликаем "Продолжить позднее"
    repeat_action('//*[contains(text(),"Продолжить позднее")]')
    # кликаем "Да"
    repeat_action('//*[text()="Да"]')
    # переключаемся на окно с результатми тестирования
    aux_func.wait_window_load_and_switch(1)  # переключаемся снова на окно с тестом
    aux_func.switch_to_frame()  # переходим на окно с результатами теста


def get_timer(driver):
    """Функция для получения значения таймера в тесте"""
    try:
        test_timer_mask = '//*[@class="timer-value quiz_main_text_timer destroyable"]'
        test_timer_val = driver.find_element(By.XPATH, test_timer_mask).get_attribute('innerText')  # оставшееся
        # время на тест (в формате MM:SS)
        test_timer_sec = int(test_timer_val.rsplit(':')[0].strip()) * 60 + int(
            test_timer_val.rsplit(':')[1].strip())  # конвертируем формат из MM:SS в секунды
        return test_timer_sec
    except Exception as ex:
        prog_logging.print_log(f'Ошибка {ex}. В тесте нет таймера', None, None, 1)
        return None


def get_clicked(weblist_data, data_dict, key):
    """Передает словарь из ID элемента и линка кликнутого ответа"""
    data = aux_functions.Dictionary(data_dict)
    answer_link = [weblist_data[key]['a_link'][0][num]
                   for num, value in enumerate(weblist_data[key]['a_checkbox'][0]) if value]  # добавляем линк
    # того же порядкового номера что и чекбокс если там есть 1
    if answer_link:  # если есть клик
        question_id = weblist_data[key]['q_id'][0]
        for each in answer_link:
            data.add_value(question_id, each)  # добавляем id вопроса и линк до ответа
