from config.init_folders import CONFIG_FILE_PATH


def read_config_file():
    try:
        with open(f'{CONFIG_FILE_PATH}', encoding='utf-8') as f:  # открытие файла с конфига
            config_raw_data = f.readlines()

    except OSError:  # если файла с конфигой нет то создаем новый
        with open(f'{CONFIG_FILE_PATH}', 'w', encoding='utf-8') as f:
            f.write(
                'answer_delay=20 # кол-во секунд на один вопрос '
                '(в проге рандомно выбирается от 0.5 до 1 частей этого значения)\n'
                'theory_delay=1 # кол-во секунд на одну теорию '
                '(в проге рандомно выбирается от 0.5 до 1 частей этого значения)'
            )
        with open(f'{CONFIG_FILE_PATH}', encoding='utf-8') as f:
            config_raw_data = f.readlines()

    return convert_config_data(config_raw_data)


def convert_config_data(config_row_data):
    config_data = {}

    config_data_without_comments = [each.split('#', 1)[0] for each in config_row_data]
    config_data_key = [each.split('=', 1)[0] for each in config_data_without_comments]
    config_data_value = [each.split('=', 1)[1].strip() for each in config_data_without_comments]

    for num, each in enumerate(config_data_key):
        config_data[each] = config_data_value[num]

    return config_data
