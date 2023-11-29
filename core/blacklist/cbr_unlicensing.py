import logging

from models import BaseDataUnit
import pandas as pd


def data_unit_iterator() -> BaseDataUnit:
    excel_table_link = "https://www.cbr.ru//vfs/finmarkets/files/supervision/list_unlicensing.xlsx"
    df = pd.read_excel(excel_table_link, storage_options={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
                                                          'Cookie': '__ddg1_=kmvDUojcEhQkFdl0ZhFW; ASPNET_SessionID=jqucbhynnzitdvejyrfzo1s2; __ddgid_=EevzvW31BB1HM0uJ; __ddgmark_=iQsD3RkyYtCcvZEz; __ddg2_=cskxdNPtKAp2xFZM; accept=1',
                                                          'Referer': 'https://www.cbr.ru/registries/'})
    for index, row in df.iterrows():
        try:
            data_unit = BaseDataUnit(
                type='black_list',
                name=row.iloc[1],
                inn=row.iloc[2],
                cbr_license_id=row.iloc[3],
                cbr_license_issue_date=row.iloc[4],
                cbr_license_period=row.iloc[5],
                cbr_license_revocation_date=row.iloc[6],
                cbr_license_revokation_reason=row.iloc[7],
                source='https://www.gov.kz/',
                country='Россия'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {row}")
