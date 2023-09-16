def func():
    return [
        '//*[@class="player-shape-view"]'
        '//*[contains(translate(text(),"абвгдежзийклмнопрстуфхцчшщъыьэюя","АБВГДЕЖЗИЙКЛМНОПРСТУФХЦЧШЩЪЫЬЭЮЯ"),'
        '"ТЕСТ")]'
    ]


print(func())
