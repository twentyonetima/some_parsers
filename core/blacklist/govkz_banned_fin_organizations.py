import logging
import json
import requests
from models import BaseDataUnit


def data_unit_iterator() -> BaseDataUnit:
    url = 'https://www.gov.kz/graphql'

    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.3',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
        'Accept-Language': 'ru',
    }

    # Identify the necessary GraphQL query
    payload = {
        'operationName': 'PermissionsTemplate6',
        'variables': {"slug": "eq:ardfm", "pageSize": 10000, "pageNumber": 1, "title": "neq:null"},
        'query': '''query PermissionsTemplate6($slug: String!, $title: String!, $pageSize: Int!, $pageNumber: Int!) {  template_permissions_6(projects: $slug, naimenovanie_bvu: $title, _size: $pageSize, _page: $pageNumber, _sort: "id:desc") {    id    naimenovanie_bvu    address    nomer_licenzii    data_vydachi    vid_operacii    data_resheniya    nomer_resheniya    osnovaniya_priostanovleniya_licenzii    posledstviya_priostanovleniya_lisheniya    transaction_currency {      id      title      __typename    }    __typename  }  _total_count {    template_permissions_6    __typename  }}'''
    }
    response = requests.post(url, headers=headers, json=payload)
    response = json.loads(response.content)

    for record in response['data']['template_permissions_6']:
        try:
            data_unit = data_transformer(record)
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {record}")


def data_transformer(record) -> BaseDataUnit:
    data_unit = BaseDataUnit(
        type='black_list',
        name=record['naimenovanie_bvu'],
        legal_entity_address=record['address'],
        govkz_current_license_id=record['nomer_licenzii'],
        govkz_current_license_date=record['data_vydachi'],
        govkz_is_foreign_or_national_currency=" ,".join([i['title'] for i in record['transaction_currency']]),
        govkz_license_revocation_decision_id=record['nomer_resheniya'],
        govkz_license_revocation_decision_date=record['data_resheniya'],
        govkz_activity_suspension_details=record['vid_operacii'],
        govkz_activity_suspension_grounds=record['osnovaniya_priostanovleniya_licenzii'],
        source='https://www.gov.kz/',
        country='Казахстан'
    )
    return data_unit


def boolean_transformer(value) -> str:  # result always as 'True' or 'False'. Why - API agreement.
    if value is True:
        return 'True'
    return 'False'

