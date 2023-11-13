import logging
import time
from datetime import datetime
import pika

from core.whitelist import (national_bank_kz, cbr_forex, cbr_reestersavers, cbr_advisors,
                            cbr_trust, cbr_specdepositaries, cbr_dealers, cbr_depositaries,
                            cbr_brokers, govkz_securities_transactions, govkz_individual_banking_transactions, bafin,
                            scm, base_1, base_3, base_5, base_9, base_10
                            )
from core.blacklist import (cbr_unlicensing, cbr_warninglist, govkz_bannedbanks, govkz_banned_fin_organizations,
                            govkz_refund_organizations, govkz_bannedbanks_2level, govkz_unfairactivity_organization,
                            govkz_new_reestr, consob, sca, amf, sfc, fsa, asc, base_2, base_6, base_11)

logging.basicConfig(
                    filename='ETL.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


WINDOW_BETWEEN_MESSAGES_SECONDS = 60 * 60 * 12
WINDOW_BETWEEN_SOURCES_SECONDS = 60


def publisher(func: callable, source_name: str) -> None:
    try:
        logging.info(f"ETL process with source <{source_name}> has been started")
        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='ETL', durable=True)

        global data_units_load_counter
        for data_unit in func:
            logging.info(data_unit)
            channel.basic_publish(exchange='',
                                  routing_key='ETL',
                                  body=data_unit
                                  )
            data_units_load_counter += 1
        logging.info(f"ETL process with source <{source_name}> has been finished. Amount of dataunits for parsing session (this parser and before them): {data_units_load_counter}")
        time.sleep(WINDOW_BETWEEN_SOURCES_SECONDS)
    except Exception as e:
        logging.error(f"Current resource was stopped cause of global error: {e}")
    finally:
        if 'connection' in locals():
            connection.close()


while True:
    data_units_load_counter = 0

    logging.info(f"Loop of scraping has been started {datetime.now()}")
    publisher(bafin.data_unit_iterator(), "BAFIN")
    publisher(consob.data_unit_iterator(), "CONSOB")
    publisher(sca.data_unit_iterator(), "Securities and Commodities Authority")
    publisher(amf.data_unit_iterator(), "AMF")
    publisher(sfc.data_unit_iterator(), "Securities and Futures Commission")
    publisher(fsa.data_unit_iterator(), "Financial Services Agency")
    publisher(asc.data_unit_iterator(), "Alberta Securities Commission")
    publisher(scm.data_unit_iterator(), "Securities Commission Malaysia")
    publisher(national_bank_kz.data_unit_iterator(), "Национальный банк РК")
    publisher(cbr_forex.data_unit_iterator(), "ЦБ РФ Список форекс-дилеров")
    publisher(cbr_reestersavers.data_unit_iterator(), "ЦБ РФ Список регистраторов")
    publisher(cbr_trust.data_unit_iterator(), "ЦБ РФ Список доверительных управляющих")
    publisher(cbr_dealers.data_unit_iterator(), "ЦБ РФ Список дилеров")
    publisher(cbr_depositaries.data_unit_iterator(), "ЦБ РФ Список депозитариев")
    publisher(cbr_brokers.data_unit_iterator(), "ЦБ РФ Список брокеров")
    publisher(cbr_specdepositaries.data_unit_iterator(), "ЦБ РФ Реестр лицензий специализированных депозитариев инвестиционных фондов, паевых инвестиционных фондов и негосударственных пенсионных фондов")
    publisher(cbr_advisors.data_unit_iterator(), "ЦБ РФ Единый реестр инвестиционных советников")
    publisher(govkz_securities_transactions.data_unit_iterator(), "GOV KZ Реестр выданных, переоформленных лицензий на проведение банковских и иных операций и осуществление деятельности на рынке ценных бумаг")
    publisher(govkz_individual_banking_transactions.data_unit_iterator(), "GOV KZ Реестр выданных, переоформленных лицензий на осуществление отдельных видов банковских операций")
    publisher(govkz_bannedbanks.data_unit_iterator(), "GOV KZ РЕЕСТР ПРИОСТАНОВЛЕННЫХ, ЛИБО ПРЕКРАТИВШИХ ДЕЙСТВИЕ (ЛИШЕННЫХ) ЛИЦЕНЗИЙ НА ПРОВЕДЕНИЕ БАНКОВСКИХ И ИНЫХ ОПЕРАЦИЙ, ОСУЩЕСТВЛЯЕМЫХ БАНКАМИ")
    publisher(govkz_banned_fin_organizations.data_unit_iterator(), "GOV KZ Реестр приостановленных, либо прекративших действие (лишенных) лицензий на осуществление отдельных видов банковских операций")
    publisher(govkz_refund_organizations.data_unit_iterator(), "GOV KZ Реестр прекративших действие лицензий организаций, осуществлявших отдельные виды банковских операций в связи с добровольным возвратом.")
    publisher(govkz_bannedbanks_2level.data_unit_iterator(), "GOV KZ Реестр прекративших действие лицензий банков второго уровня в связи с добровольным возвратом")
    publisher(govkz_unfairactivity_organization.data_unit_iterator(), "GOV KZ Список организаций, имеющих признаки недобросовестной деятельности")
    publisher(cbr_unlicensing.data_unit_iterator(), "ЦБ РФ Реестр аннулированных лицензий профессиональных участников рынка ценных бумаг")
    publisher(cbr_warninglist.data_unit_iterator(), "ЦБ РФ Список компаний с выявленными признаками нелегальной деятельности на финансовом рынке")
    publisher(govkz_new_reestr.data_unit_iterator(), "Реестр финансовых пирамид")
    publisher(base_1.data_unit_iterator(), "FMA Лицензированные и подотчетные лица")
    publisher(base_2.data_unit_iterator(), "FMA Предупреждения и оповещения")
    publisher(base_3.data_unit_iterator(), "Реестр утвержденных ценных бумаг Финляндия")
    publisher(base_5.data_unit_iterator(), "Реестр поставщиков финансовых услуг")
    publisher(base_6.data_unit_iterator(), "Предупреждения и оповещения инвесторов Канады")
    publisher(base_9.data_unit_iterator(), "Реестр уполномоченных лиц Андорры")
    publisher(base_10.data_unit_iterator(), "Список PSAN, зарегистрированных в AMF")
    publisher(base_11.data_unit_iterator(), "Реестр защиты украинских инвесторов")

    logging.info(f"Loop of scraping has been finished {datetime.now()}")
    time.sleep(WINDOW_BETWEEN_MESSAGES_SECONDS)
