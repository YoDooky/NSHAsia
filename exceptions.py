class NoFoundedElement(Exception):
    def __init__(self, text):
        self.text = text
        super().__init__(
            f'Элемент <{self.text}> не найден на вебстранице')


class NotSupportedDataType(Exception):
    def __init__(self):
        super().__init__(
            f'Отсутствует соотношение между типом данных и SQL таблицей')


class MaxVariantsExceeded(Exception):
    def __init__(self):
        super().__init__(
            f'Превышено максимальное количество возможных переборов ответов')


class ImpossibleToClick(Exception):
    def __init__(self):
        super().__init__(
            f'Невозможно кликнуть по ответу')


class NoDataToWrite(Exception):
    def __init__(self):
        super().__init__(
            f'Во временной базе данных нет правильных ответов для записи в постоянную базу')


class NoAnswerResult(Exception):
    """Exception for question solve result"""

    def __init__(self):
        super().__init__('Не могу оценить результат решения вопроса (правильно/неправильно)')
