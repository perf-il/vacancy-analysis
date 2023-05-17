import json
from os import path

employers = ['СБЕР', 'ВТБ', 'Тинькофф', 'Яндекс', 'Вконтакте', 'Skillbox', 'МТС', 'Skyeng', 'Тензор', 'Альпинтех']


def get_selected_employers_id():
    """функция для получения отобранных id компаний"""
    with open(path.join('data', 'selected_employers_id.json'), encoding='utf-8') as f:
        selected_id = json.load(f)
    return selected_id


def get_str_from_list(list_id: list) -> str:
    """
    функция-представление списка id в формате для SQL-запроса
    :param list_id: список id
    :return: строка в формате ('ID1', 'ID2', ..., 'IDn')
    """
    str_from_list = '('
    for num in list_id:
        str_from_list += f"'{num}', "
    str_from_list = str_from_list[:-2] + ')'
    return str_from_list


def change_ap(word: str) -> str:
    """
    Функция для изменения типа кавычек в названии, для формирования корректного SQL-запроса
    """
    if word.count("'") == 0:
        return word
    return word.replace("'", '"')


