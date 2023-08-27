import os


class Folders:
    # main path
    FILES_PATH = "C:/NSHAsia"

    # chromedriver path
    DRIVER_PATH = f'{FILES_PATH}/driver'

    # DB folder
    DB_PATH = f'{FILES_PATH}/database'

    # audio folder
    AUDIO_PATH = f'{FILES_PATH}/audio'

    # log path
    LOG_PATH = f'{FILES_PATH}/log'  # путь до папки с клиентами

    # config file path
    CONFIG_PATH = f'{FILES_PATH}/config'

    @classmethod
    def init_folders(cls):
        cls_paths = [value for key, value in cls.__dict__.items() if
                     not callable(value) and not key.startswith('__') and not isinstance(value, classmethod)]
        for path in cls_paths:
            try:
                os.makedirs(f'{path}')
            except FileExistsError:
                pass
            pass


Folders.init_folders()

MUSIC_FILE_PATH = f'{Folders.AUDIO_PATH}/heyuser.mp3'  # путь до звукового файла
ALARM_FILE_PATH = f'{Folders.AUDIO_PATH}/alarm.mp3'  # путь до звукового файла с пиздец каким алармом
CHROMEDRIVER_PATH = f'{Folders.DRIVER_PATH}/chromedriver.exe'
CONFIG_FILE_PATH = f'{Folders.CONFIG_PATH}/config.txt'
LOG_FILE_PATH = f'{Folders.LOG_PATH}/log.txt'
