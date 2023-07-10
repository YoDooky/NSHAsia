import os

# main folder
files_path = "C:/NSHAsia"

# chromedriver path
driver_path = f'{files_path}/driver'
chromedriver_path = f'{driver_path}/chromedriver.exe'

# DB folder
db_path = f'{files_path}/database'

# audio folder
audio_path = f'{files_path}/audio'
music_path = f'{audio_path}/heyuser.mp3'  # путь до звукового файла
alarm_music_path = f'{audio_path}/alarm.mp3'  # путь до звукового файла с пиздец каким алармом

# log path
log_path = f'{files_path}/log'  # путь до папки с клиентами


def init_folders():
    """try to create folders"""
    for path in [files_path, driver_path, db_path, audio_path, log_path]:
        try:
            os.makedirs(f'{path}')
        except FileExistsError:
            pass
        pass
