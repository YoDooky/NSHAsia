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
        super().__init__(
            'Не могу оценить результат решения вопроса (правильно/неправильно)')


class NoSelectedAnswer(Exception):
    """Exception if there is no selected answers"""

    def __init__(self):
        super().__init__(
            'Не могу увидеть выбранные ответы. Скорее всего не верный путь для проверки кликнутых ответов')


class TheoryNotChanges(Exception):
    """Exception if theory page doesn't change"""

    def __init__(self):
        super().__init__(
            'Окно с теорией не изменяется. Скорее всего из-за конца темы')


class QuizEnded(Exception):
    """Exception to check if quiz has been ended"""

    def __init__(self):
        super().__init__(
            'Новые вопросы не появляются. Скорее всего из-за конца темы')


class CantFindResultPage(Exception):
    """"""

    def __init__(self):
        super().__init__(
            'Не могу найти экран с результатами')
