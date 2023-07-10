class NoFoundedElement(Exception):
    def __init__(self, text):
        self.text = text
        super().__init__(
            f'Ссылка для клика на ответ <{self.text}> не найдена на вебстранице')
