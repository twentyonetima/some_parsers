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
        'operationName': 'PermissionsTemplate5',
        'variables': {"slug": "eq:ardfm", "pageSize": 10000, "pageNumber": 1, "title": "neq:null"},
        'query': '''query PermissionsTemplate5($slug: String!, $title: String!, $pageSize: Int!, $pageNumber: Int!) {  template_permissions_5(projects: $slug, title: $title, _size: $pageSize, _page: $pageNumber, _sort: "id:desc") {    id    title    location    data_resheniya    nomer_resheniya    nomer_licenzii    data_vydachi    vid_deyatelnosti    transaction_currency {      id      title      __typename    }    __typename  }  info_block(projects: $slug, code: "eq:template_permissions_5_info") {    id    text    __typename  }}'''
    }
    response = requests.post(url, headers=headers, json=payload)
    response = json.loads(response.content)

    for record in response['data']['template_permissions_5']:
        try:
            data_unit = data_transformer(record)
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {record}")


def data_transformer(record) -> BaseDataUnit:
    data_unit = BaseDataUnit(
        type='black_list',
        name=record['title'],
        legal_entity_address=record['location'],
        govkz_current_license_id=record['nomer_licenzii'],
        govkz_current_license_date=record['data_vydachi'],
        govkz_type_of_activity=record['vid_deyatelnosti'],
        govkz_is_foreign_or_national_currency=" ,".join([i['title'] for i in record['transaction_currency']]),
        govkz_license_revocation_decision_id=record['nomer_resheniya'] if isinstance(record['nomer_resheniya'], str) else "",
        govkz_license_revocation_decision_date=record['data_resheniya'],
        source='https://www.gov.kz/',
        country='Казахстан'
    )
    return data_unit


def boolean_transformer(value) -> str:  # result always as 'True' or 'False'. Why - API agreement.
    if value is True:
        return 'True'
    return 'False'

