# from db.controllers import WebDataController, TempDbDataController
# import itertools
# import re
#
# web_data = WebDataController().read_data()
#
# '3. На 6.'
# '3. На 6.'
#
#
# def del_spec_symbols(text: str) -> str:
#     spec_symbols_accord = {'\xa0': ' ', '\u200b': ''}
#     for symbol in spec_symbols_accord:
#         text = text.replace(symbol, spec_symbols_accord.get(symbol))
#     return ' '.join(text.split())


from log import init_logging_config, print_log
import logging

init_logging_config()


def func(val):
    try:
        return val / 2
    except Exception as ex:
        print_log(f'Ошибка: {ex}. Возникла проблема при решении курса. Пробую еще раз')
        logging.exception("An error")


func('')
