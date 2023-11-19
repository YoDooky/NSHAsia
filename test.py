import time
from dataclasses import dataclass

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.webelement import WebElement

from driver_init import driver
from web import XpathResolver

INPUT_DATA = {
    'компания': 'ООО НСХ Азия дрилинг',
    'должность': 'Пом. бурильщика КРС 5р',
    'телефон': '89222886027',
    'адрес': 'г. Муравленко, ул. Муравленко, д. 6, кв. 22'
}


@dataclass
class FormField:
    input_name: str
    input_link: WebElement


def get_form_data():
    def parse_string(string: str) -> str:
        """Returns only alphabetic characters from string"""
        return ''.join([char.lower() for char in string if char.isalpha()])

    input_name_mask = '//*[@class="field-view"]'
    input_name_fields = driver.find_elements(By.XPATH, input_name_mask)

    input_link_mask = '//*[@class="field-view"]/input'
    input_link_fields = driver.find_elements(By.XPATH, input_link_mask)

    return [FormField(
        input_name=parse_string(name.text),
        input_link=link
    ) for name, link in zip(input_name_fields, input_link_fields)]


def main():
    # AuxFunc().try_click(XpathResolver.start_button())

    try:
        driver.get('E:/Downloads/Итоговый тест..html')
        driver.switch_to.window(driver.window_handles[-1])
        driver.switch_to.frame(driver.find_element(By.XPATH, XpathResolver.iframe()))
        for data in get_form_data():
            if data.input_name in INPUT_DATA:
                data.input_link.send_keys(INPUT_DATA[data.input_name])
            time.sleep(1)

        element = driver.find_element(By.XPATH, XpathResolver.answer_button())
        element.click()
    except Exception as ex:
        driver.quit()


if __name__ == '__main__':
    main()
    driver.quit()
