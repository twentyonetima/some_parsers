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
        'operationName': 'PermissionsTemplate4',
        'variables': {"slug": "eq:ardfm", "pageSize": 10000, "pageNumber": 1, "title": "neq:null"},
        'query': '''query PermissionsTemplate4($slug: String!, $title: String!, $pageSize: Int!, $pageNumber: Int!) {  template_permissions_4(projects: $slug, title: $title, _size: $pageSize, _page: $pageNumber, _sort: "id:desc") {    id    organization_type {      id      title      __typename    }    title    number    data_vydachi    nomer_resheniya    data_resheniya    v_tenge_i_iv    kolichestvo_bankovskih_operaciy    priem_depozitov_yuridicheskih_lic    priem_depozitov_fizicheskih_lic    otkrytie_kor_schetov    otkrytie_schetov_yuridicheskih_lic    kassovye_operacii    perevodnye_operacii    bankovskie_operacii    obmennye_operacii    doveritelnye_operacii    vypusk_cennyh_bumag    faktoringovye_operacii    nomer_pervichnoy_licenzii    data_pervichnoy_licenzii    current_date_info {      action_type {        id        name        __typename      }      osnovaniya_vydachi      operations_license_issued      money_type      __typename    }    fin_org {      bin      __typename    }    __typename  }}'''
    }
    response = requests.post(url, headers=headers, json=payload)
    response = json.loads(response.content)

    for record in response['data']['template_permissions_4']:
        try:
            data_unit = data_transformer(record)
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {record}")


def data_transformer(record) -> BaseDataUnit:
    data_unit = BaseDataUnit(
        type='white_list',
        bin=record['fin_org']['bin'],
        name=record['title'],
        organizational_and_legal_form=record['organization_type']['title'],  # a crutch on the graphql side
        # legal_entity_address=record['location'],
        govkz_license=record['number'],
        govkz_license_decision_date=record['data_resheniya'] if isinstance(record['data_resheniya'], str) else "",
        govkz_license_official_order=record['nomer_resheniya'],
        govkz_primary_license_id=record['nomer_pervichnoy_licenzii'],
        govkz_primary_license_date=record['data_pervichnoy_licenzii'],
        govkz_current_license_id=record['number'],
        govkz_current_license_date=record['data_resheniya'],
        govkz_is_foreign_or_national_currency=record['v_tenge_i_iv'],
        govkz_banking_operations_provision_counter=str(record['kolichestvo_bankovskih_operaciy']),
        govkz_banking_is_parameter1=boolean_transformer(record['priem_depozitov_yuridicheskih_lic']),
        govkz_banking_is_parameter2=boolean_transformer(record['priem_depozitov_yuridicheskih_lic']),
        govkz_banking_is_parameter6=boolean_transformer(record['kassovye_operacii']),
        govkz_banking_is_parameter7=boolean_transformer(record['perevodnye_operacii']),
        govkz_banking_is_parameter20=boolean_transformer(record['vypusk_cennyh_bumag']),
        govkz_banking_is_parameter21=boolean_transformer(record['faktoringovye_operacii']),
        govkz_banking_is_parameter61=boolean_transformer(record['doveritelnye_operacii']),
        govkz_banking_is_parameter62=boolean_transformer(record['obmennye_operacii']),
        govkz_banking_is_parameter63=boolean_transformer(record['otkrytie_kor_schetov']),
        govkz_banking_is_parameter64=boolean_transformer(record['otkrytie_schetov_yuridicheskih_lic']),
        govkz_banking_is_parameter65=boolean_transformer(record['faktoringovye_operacii']),
        source='https://www.gov.kz/',
        country='Казахстан'
    )
    return data_unit


def boolean_transformer(value) -> str:  # result always as 'True' or 'False'. Why - API agreement.
    if value is True:
        return 'True'
    return 'False'

