#! python
# -*- coding: utf-8 -*-

"""Cоздаём резервную копию файлов с переносного диска (флэшки).

Настройки работы скрипта хранятся в переменных окружения.
"""

import os
import time
import subprocess
# pip install psutil
import psutil

# Импорт переменных окружения
from dotenv import load_dotenv
load_dotenv(verbose=True)

start_time = time.time()

# Параметры работы берутся из переменных окружения
EXE = os.getenv('EXE')
SOURCE = os.getenv('SOURCE')
TARGET_DIR = os.getenv('TARGET_DIR')


def check_target_dir() -> None:
    """Проверяем создана ли директория TARGET_DIR.

    Директория TARGET_DIR - целевая для хранения бэкап-файлов,
    если таковая отсутствует - то функция её создаёт.
    """
    if not os.path.exists(TARGET_DIR):
        os.mkdir(TARGET_DIR)
        print('Директория для хранения резервных копий успешно создана!')
    print(f'Директория хранения резерных копий: {TARGET_DIR}')


def create_target_name() -> str:
    """Функция возвращает имя архива.

    Имя архива это абсолютный путь до бэкап-файла
    в формате '%Y%m%d_%H%M%S.7z'.
    """
    today = time.strftime('%Y%m%d') + '_' + time.strftime('%H%M%S')
    target_name = TARGET_DIR + os.sep + today + '.7z'
    print(f'Имя бэкап-файла: {target_name}')
    return target_name


def create_sevenzip_archive(exe: str, target: str, source: str) -> tuple:
    """Функция запускает отдельный процесс, создающий сжатый архив.

    Функция возвращает кортеж от результатов работы
    метода communicate (нужно для исключения deadlock).
    """
    cmd = [exe, 'a', target, source, '-mx9']
    process = subprocess.Popen(
        cmd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True)
    data = process.communicate()
    return data


def backup_logging(data_from_process: tuple, target_name: str) -> None:
    """Функция выводит информацию по работе скрипта в консоль."""
    if data_from_process[1] is None:
        source_size = get_size(psutil.disk_usage(SOURCE).used)
        print(f'Размер файлов источника {SOURCE}\\ {source_size}')
        target_size = get_size(os.path.getsize(target_name))
        print(f'Размер созданного архива: {target_size}')
    else:
        print('Что-то пошло не так...')
    script_msg = 'Работа по резервированию данных окончена!\n'
    script_msg += f'Прошло {time.time() - start_time: .2f} секунд'
    print(script_msg)


def get_size(size: float, suffix='B') -> str:
    """Фукнция приведения размера к читабельному формату.

    Функция принимает значение в байтах и приводит их в
    читабельное значение - Кб, Мб, Гб...
    """
    factor = 1024
    for unit in ['', 'K', 'M', 'G', 'T', 'P']:
        if size < factor:
            return f'{size: .2f} {unit}{suffix}'
        size /= factor


def main():
    """Основная функция скрипта.

    В ней проприсана последовательность дейтсвий по созданию бэкап-файла.
    """
    check_target_dir()
    target_name = create_target_name()
    data = create_sevenzip_archive(EXE, target_name, SOURCE)
    backup_logging(data, target_name)


if __name__ == '__main__':
    main()
