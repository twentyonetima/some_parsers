import json


def save_json(data):
    """
    Метод сохранения полученных данных в формат json
    :param data:
    :return:
    """
    with open("jsonFiles.json", "w", encoding='utf-8') as fl:
        json.dump(fp=fl, indent=4, obj=data, ensure_ascii=False)
