# -*- coding: utf-8 -*-
import os
import patoolib

DIRECTORY = "./data/excels"

def get_excel_files(directory=DIRECTORY,delimiter='\n'):
    excel_files = []
    for filename in os.listdir(directory):
        if filename.endswith(".xlsx"):
            excel_files.append(filename)
    return delimiter.join(excel_files)


def check_text_in_response(text_to_check, directory=DIRECTORY, delimiter='\n'):
    response = get_excel_files(directory, delimiter)
    return text_to_check in response

def format_excel_name(excel_name):
    return "./data/" + excel_name

def clear_folder(folder_path = "./data/excels"):

    # Получаем список файлов в папке
    files = os.listdir(folder_path)
    # Проходимся по всем файлам в папке
    for file_name in files:
        # Получаем полный путь к файлу
        file_path = os.path.join(folder_path, file_name)
        # Проверяем, является ли объект файлом
        if os.path.isfile(file_path):
            # Удаляем файл
            os.remove(file_path)
            print(f"Файл {file_path} удален.")
        else:
            print(f"Объект {file_path} не является файлом и не будет удален.")


def extract_rar_to_excels(rar_file_path):
    # Создаем папку для сохранения извлеченных файлов, если она не существует
    patoolib.extract_archive(rar_file_path, outdir = './data/excels')
    os.remove(rar_file_path)