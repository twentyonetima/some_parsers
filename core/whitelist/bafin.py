import requests
import csv
import json

from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = ('https://portal.mvp.bafin.de/database/InstInfo/'
           'sucheForm.do?d-4012550-p=142&6578706f7274=1&sucheButtonInstitut=Suche&d-4012550-e=1')
    response = requests.get(url)

    with open('file.csv', 'wb') as f:
        f.write(response.content)

    with open('file.csv', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        rows = list(reader)

    with open('file.json', 'w') as f:
        json.dump(rows, f)

    file = open("file.json")
    a = file.read().replace(':', ';')
    a = a.split(';')

    sublists = [a[i:i + 8] for i in range(0, len(a), 8)]
    result = {}

    for i in range(len(sublists) - 1):
        merged_list = [
            f"{x}:{y}, 'type': 'white_list', 'source': 'https://portal.mvp.bafin.de/database/InstInfo/sucheForm.do?d-4012550-p=142&6578706f7274=1&sucheButtonInstitut=Suche&d-4012550-e=1' "
            for x, y in zip(sublists[i], sublists[i + 1])]
        result[f"list_{i + 1}"] = merged_list
