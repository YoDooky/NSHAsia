import time
from functools import wraps
from playsound import playsound
from decohints import decohints

from config import MUSIC_FILE_PATH
from log import print_log


class FunctionTry:
    """ Trying to call user function decorator """
    MAX_TRY_NUMB = 3

    def __init__(self, message_to_user: str):
        """
        :param message_to_user: message to user, if fucntion can't be done
        """
        self.message_to_user = message_to_user

    @decohints
    def __call__(self, func):
        """
        :param func: function to call
        :return: None
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            for i in range(0, self.MAX_TRY_NUMB + 1):
                try:
                    return func(*args, **kwargs)
                except Exception as ex:
                    print_log(exception=ex, silent=True)
                    time.sleep(1)
                    if i >= self.MAX_TRY_NUMB:
                        playsound(MUSIC_FILE_PATH)
                        input(f'{self.message_to_user}'
                              f'\nНажми <Enter> чтобы продолжить...')

        return wrapper
