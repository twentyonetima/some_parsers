import logging
import math

from models import BaseDataUnit
import pandas as pd


def data_unit_iterator() -> BaseDataUnit:
    excel_table_link = "https://www.cbr.ru/vfs/finmarkets/files/supervision/List_is.xlsx"
    df = pd.read_excel(excel_table_link, storage_options={'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/118.0',
                                                          'Cookie': '__ddg1_=kmvDUojcEhQkFdl0ZhFW; ASPNET_SessionID=jqucbhynnzitdvejyrfzo1s2; __ddgid_=EevzvW31BB1HM0uJ; __ddgmark_=iQsD3RkyYtCcvZEz; __ddg2_=cskxdNPtKAp2xFZM; accept=1',
                                                          'Referer': 'https://www.cbr.ru/registries/'})
    for index, row in df.iterrows():
        if type(row.iloc[0]) is float or not (row.iloc[0]).isdigit():
            continue
        try:
            data_unit = BaseDataUnit(
                type='white_list',
                name=row.iloc[2] if isinstance(row.iloc[2], str) or not math.isnan(row.iloc[2]) else '',
                name_full=row.iloc[1] if isinstance(row.iloc[1], str) or not math.isnan(row.iloc[1]) else '',
                legal_entity_address=row.iloc[5] if isinstance(row.iloc[5], str) or not math.isnan(row.iloc[5]) else '',
                links=[row.iloc[6]] if isinstance(row.iloc[6], str) or not math.isnan(row.iloc[6]) else '',
                phones=row.iloc[7] if isinstance(row.iloc[7], str) or not math.isnan(row.iloc[7]) else '',
                email=row.iloc[8] if isinstance(row.iloc[8], str) or not math.isnan(row.iloc[8]) else '',
                cbr_counselor_license_issue_date=row.iloc[9] if isinstance(row.iloc[9], str) or not math.isnan(row.iloc[9]) else '',
                source='https://cbr.ru',
                country='Россия'
            )
            yield data_unit.model_dump_json()
        except Exception as e:
            logging.error(e)
            logging.error(f"Error while atempt to transform following row {row}")
