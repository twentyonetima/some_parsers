import logging
import time
from datetime import datetime
import pika

from core.whitelist import (national_bank_kz, cbr_forex, cbr_reestersavers, cbr_advisors,
                            cbr_trust, cbr_specdepositaries, cbr_dealers, cbr_depositaries,
                            cbr_brokers, govkz_securities_transactions, govkz_individual_banking_transactions, scm,
                            )
from core.blacklist import (cbr_unlicensing, cbr_warninglist, govkz_bannedbanks, govkz_banned_fin_organizations,
                            govkz_refund_organizations, govkz_bannedbanks_2level, govkz_unfairactivity_organization)

logging.basicConfig(
                    filename='ETL.log',
                    encoding='utf-8',
                    level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s',
                    datefmt='%m/%d/%Y %I:%M:%S %p')


connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
channel = connection.channel()

channel.queue_declare(queue='ETL', durable=True)

WINDOW_BETWEEN_MESSAGES_SECONDS = 60 * 60 * 12

COUNTER = 1


def publisher(func: callable, source_name: str) -> None:
    try:
        logging.info(f"ETL process with source <{source_name}> has been started")
        global COUNTER
        for data_unit in func:
            logging.info(data_unit)
            channel.basic_publish(exchange='',
                                  routing_key='ETL',
                                  body=data_unit
                                  )
            COUNTER += 1
        logging.info(f"ETL process with source <{source_name}> has been finished. Amount of dataunits: {COUNTER}")
        time.sleep(60)
    except Exception as e:
        logging.error(f"Current resource was stopped cause of global error: {e}")


while True:
    logging.info(f"Loop of scraping has been started {datetime.now()}")
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
    publisher(govkz_bannedbanks_2level.data_unit_iterator(), "GOV KZ РЕЕСТР ПРИОСТАНОВЛЕННЫХ, ЛИБО ПРЕКРАТИВШИХ ДЕЙСТВИЕ (ЛИШЕННЫХ) ЛИЦЕНЗИЙ НА ПРОВЕДЕНИЕ БАНКОВСКИХ И ИНЫХ ОПЕРАЦИЙ, ОСУЩЕСТВЛЯЕМЫХ БАНКАМИ")
    publisher(govkz_banned_fin_organizations.data_unit_iterator(), "GOV KZ Реестр приостановленных, либо прекративших действие (лишенных) лицензий на осуществление отдельных видов банковских операций")
    publisher(govkz_refund_organizations.data_unit_iterator(), "GOV KZ Реестр прекративших действие лицензий организаций, осуществлявших отдельные виды банковских операций в связи с добровольным возвратом.")
    publisher(govkz_refund_organizations.data_unit_iterator(), "GOV KZ Реестр прекративших действие лицензий банков второго уровня в связи с добровольным возвратом")
    publisher(govkz_unfairactivity_organization.data_unit_iterator(), "GOV KZ Список организаций, имеющих признаки недобросовестной деятельности")
    publisher(cbr_unlicensing.data_unit_iterator(), "ЦБ РФ Реестр аннулированных лицензий профессиональных участников рынка ценных бумаг")
    publisher(cbr_warninglist.data_unit_iterator(), "ЦБ РФ Список компаний с выявленными признаками нелегальной деятельности на финансовом рынке")

    logging.info(f"Loop of scraping has been finished {datetime.now()}")
    time.sleep(WINDOW_BETWEEN_MESSAGES_SECONDS)
