class NoFoundedElement(Exception):
    def __init__(self, text):
        self.text = text
        super().__init__(
            f'Элемент <{self.text}> не найден на вебстранице')


class NotSupportedDataType(Exception):
    def __init__(self):
        super().__init__(
            f'Отсутствует соотношение между типом данных и SQL таблицей')

