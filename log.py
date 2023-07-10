import logging
from config.folders import log_path


def print_log(message, sep=None, end=None, silent=None):
    if not silent:
        if sep:
            if end:
                print(message, sep, end)
            else:
                print(message, sep)
        else:
            print(message)

    # создаем файл с логами если еще не создали
    log_file = f'{log_path}/log.txt'
    try:
        with open(log_file, 'x') as f:
            f.write('')
    except FileExistsError:
        pass
    logging.basicConfig(filename=log_file,
                        filemode='a',
                        format='%(asctime)s %(name)s [%(levelname)s] %(message)s',
                        datefmt='%Y-%m-%d,%H:%M:%S',
                        level=logging.DEBUG)
    logging.debug(message)
