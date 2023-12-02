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
        'operationName': 'PermissionsTemplate8',
        'variables': {"slug": "eq:ardfm", "pageSize": 10000, "pageNumber": 1, "title": "neq:null"},
        'query': '''query PermissionsTemplate8($slug: String!, $title: String!, $pageSize: Int!, $pageNumber: Int!) {  template_permissions_8(projects: $slug, title: $title, _size: $pageSize, _page: $pageNumber, _sort: "id:desc") {    id    fin_org {      bin      __typename    }    fin_org_type {      id      title      __typename    }    title    location    svedeniya_registracii    data_resheniya    nomer_resheniya    nomer_licenzii    data_vydachi_licenzii    nacionalnaya_valyuta    kol_vo_operaciy    priem_depozitov_yuridicheskih_lic    priem_depozitov_fizicheskih_lic    otkrytie_korrespondentskih_schetov    otkrytie_metallicheskih_schetov    kassovye_operacii    perevodnye_operacii    uchetnye_operacii    bankovskie_zamenyaemye_operacii    inkasaciya_banknot    obmennye_operacii    priem_na_inkasso    otkrytie_akkreditiva    vydacha_bankovskih_garantiy    vydacha_bankovskih_poruchitelstv    pokupka_priem_v_zalog    pokupka_yuvelirnyh_izdeliy    operacii_s_vekselyami    lizing    vypusk_cennyh_bumag    faktoringovye_operacii    forfeytingovye_operacii    seyfovye_operacii    upravlenie_dragocennymi_metallami    upravlenie_dengami    upravlenie_pravami_trebovaniya    kastodialnaya_deyatelnost    transfer    brokerskaya_deyatelnost_s_pravom    brokerskaya_deyatelnost_bez_prava    dilerskaya_deyatelnost    priem_besprocentnyh_depozitov    priem_investicionnyh_depozitov    bankovskie_zaemnye_operacii    bez_usloviya    na_usloviyah    finansirovanie_proizvodstvennoy    investicionnaya_deyatelnost    agentskaya_deyatelnost    priem_depozitov_fiz_yur    emissiya    priem_vkladov_depozitov    predostavlenie_vkladchikam    priem_vkladov_zhilishchnyh_zaymov    temp_payment    nomer_pervichnoy_licenzii    data_pervichnoy_licenzii    current_date_info {      action_type {        id        name        __typename      }      osnovaniya_vydachi      operations_license_issued      money_type      __typename    }    priem_vkladov_depozitov_otb    pvz_otb    pvo_otb    ovtb_otb    kopv_otb    povp_otb    ooiv_otb    pdov_otb    ovtbf_otb    escb_otb    doup_otb    ddnr_otb    ddnrcbspvskvknd    ddrcbbpvskvknd    banking_operations    other_operations    __typename  }  info_block(projects: $slug, code: "eq:template_permissions_8_info") {    id    text    __typename  }}'''
    }
    response = requests.post(url, headers=headers, json=payload)
    response = json.loads(response.content)

    for record in response['data']['template_permissions_8']:
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
        organizational_and_legal_form=record['fin_org_type'][0]['title'],  # a crutch on the graphql side
        legal_entity_address=record['location'],
        govkz_license=record['svedeniya_registracii'],
        govkz_license_decision_date=record['data_resheniya'] if isinstance(record['data_resheniya'], str) else "",
        govkz_license_official_order=record['nomer_resheniya'],
        govkz_primary_license_id=record['nomer_pervichnoy_licenzii'],
        govkz_primary_license_date=record['data_pervichnoy_licenzii'],
        govkz_current_license_id=record['nomer_licenzii'],
        govkz_current_license_date=record['data_vydachi_licenzii'],
        govkz_is_foreign_or_national_currency=record['nacionalnaya_valyuta'],
        govkz_banking_operations_provision_counter=str(record['kol_vo_operaciy']),
        govkz_banking_is_parameter1=boolean_transformer(record['priem_depozitov_yuridicheskih_lic']),
        govkz_banking_is_parameter2=boolean_transformer(record['priem_depozitov_yuridicheskih_lic']),
        govkz_banking_is_parameter3=boolean_transformer(record['priem_depozitov_fizicheskih_lic']),
        govkz_banking_is_parameter4=boolean_transformer(record['otkrytie_korrespondentskih_schetov']),
        govkz_banking_is_parameter5=boolean_transformer(record['otkrytie_metallicheskih_schetov']),
        govkz_banking_is_parameter6=boolean_transformer(record['kassovye_operacii']),
        govkz_banking_is_parameter7=boolean_transformer(record['perevodnye_operacii']),
        govkz_banking_is_parameter8=boolean_transformer(record['uchetnye_operacii']),
        govkz_banking_is_parameter9=boolean_transformer(record['bankovskie_zamenyaemye_operacii']),
        govkz_banking_is_parameter10=boolean_transformer(record['inkasaciya_banknot']),
        govkz_banking_is_parameter11=boolean_transformer(record['obmennye_operacii']),
        govkz_banking_is_parameter12=boolean_transformer(record['priem_na_inkasso']),
        govkz_banking_is_parameter13=boolean_transformer(record['otkrytie_akkreditiva']),
        govkz_banking_is_parameter14=boolean_transformer(record['vydacha_bankovskih_garantiy']),
        govkz_banking_is_parameter15=boolean_transformer(record['vydacha_bankovskih_poruchitelstv']),
        govkz_banking_is_parameter16=boolean_transformer(record['pokupka_priem_v_zalog']),
        govkz_banking_is_parameter17=boolean_transformer(record['pokupka_yuvelirnyh_izdeliy']),
        govkz_banking_is_parameter18=boolean_transformer(record['operacii_s_vekselyami']),
        govkz_banking_is_parameter19=boolean_transformer(record['lizing']),
        govkz_banking_is_parameter20=boolean_transformer(record['vypusk_cennyh_bumag']),
        govkz_banking_is_parameter21=boolean_transformer(record['faktoringovye_operacii']),
        govkz_banking_is_parameter22=boolean_transformer(record['forfeytingovye_operacii']),
        govkz_banking_is_parameter23=boolean_transformer(record['seyfovye_operacii']),
        govkz_banking_is_parameter24=boolean_transformer(record['upravlenie_dragocennymi_metallami']),
        govkz_banking_is_parameter25=boolean_transformer(record['upravlenie_dengami']),
        govkz_banking_is_parameter26=boolean_transformer(record['upravlenie_pravami_trebovaniya']),
        govkz_banking_is_parameter27=boolean_transformer(record['kastodialnaya_deyatelnost']),
        govkz_banking_is_parameter28=boolean_transformer(record['transfer']),
        govkz_banking_is_parameter29=boolean_transformer(record['brokerskaya_deyatelnost_s_pravom']),
        govkz_banking_is_parameter30=boolean_transformer(record['brokerskaya_deyatelnost_bez_prava']),
        govkz_banking_is_parameter31=boolean_transformer(record['dilerskaya_deyatelnost']),
        govkz_banking_is_parameter32=boolean_transformer(record['priem_besprocentnyh_depozitov']),
        govkz_banking_is_parameter33=boolean_transformer(record['priem_investicionnyh_depozitov']),
        govkz_banking_is_parameter34=boolean_transformer(record['bankovskie_zaemnye_operacii']),
        govkz_banking_is_parameter35=boolean_transformer(record['bez_usloviya']),
        govkz_banking_is_parameter36=boolean_transformer(record['na_usloviyah']),
        govkz_banking_is_parameter37=boolean_transformer(record['finansirovanie_proizvodstvennoy']),
        govkz_banking_is_parameter38=boolean_transformer(record['investicionnaya_deyatelnost']),
        govkz_banking_is_parameter39=boolean_transformer(record['agentskaya_deyatelnost']),
        govkz_banking_is_parameter40=boolean_transformer(record['priem_depozitov_fiz_yur']),
        govkz_banking_is_parameter41=boolean_transformer(record['emissiya']),
        govkz_banking_is_parameter42=boolean_transformer(record['priem_vkladov_depozitov']),
        govkz_banking_is_parameter43=boolean_transformer(record['predostavlenie_vkladchikam']),
        govkz_banking_is_parameter44=boolean_transformer(record['priem_vkladov_zhilishchnyh_zaymov']),
        govkz_banking_is_parameter45=boolean_transformer(record['priem_vkladov_depozitov_otb']),
        govkz_banking_is_parameter46=boolean_transformer(record['pvz_otb']),
        govkz_banking_is_parameter47=boolean_transformer(record['pvo_otb']),
        govkz_banking_is_parameter48=boolean_transformer(record['ovtb_otb']),
        govkz_banking_is_parameter49=boolean_transformer(record['kopv_otb']),
        govkz_banking_is_parameter50=boolean_transformer(record['povp_otb']),
        govkz_banking_is_parameter51=boolean_transformer(record['ooiv_otb']),
        govkz_banking_is_parameter52=boolean_transformer(record['pdov_otb']),
        govkz_banking_is_parameter53=boolean_transformer(record['ovtbf_otb']),
        govkz_banking_is_parameter54=boolean_transformer(record['escb_otb']),
        govkz_banking_is_parameter55=boolean_transformer(record['doup_otb']),
        govkz_banking_is_parameter56=boolean_transformer(record['ddnr_otb']),
        govkz_banking_is_parameter57=boolean_transformer(record['ddnrcbspvskvknd']),
        govkz_banking_is_parameter58=boolean_transformer(record['ddrcbbpvskvknd']),
        govkz_banking_is_parameter59=boolean_transformer(record['banking_operations']),
        govkz_banking_is_parameter60=boolean_transformer(record['other_operations']),
        source='https://www.gov.kz/',
        country='Казахстан'
    )
    return data_unit


def boolean_transformer(value) -> str:  # result always as 'True' or 'False'. Why - API agreement.
    if value is True:
        return 'True'
    return 'False'
