import logging
import time
from datetime import datetime
from typing import Union, Any

import pika
from dotenv import dotenv_values

import telebot

from models import BaseDataUnit

env = dotenv_values(".env")

tg_bot = telebot.TeleBot(env.get('BOT_TOKEN', -1))

from core.whitelist import (national_bank_kz, cbr_forex, cbr_reestersavers, cbr_advisors,
                            cbr_trust, cbr_specdepositaries, cbr_dealers, cbr_depositaries,
                            cbr_brokers, govkz_securities_transactions, govkz_individual_banking_transactions, bafin,
                            scm, fma_govt_nz_business, finanssivalvonta, registers_centralbank_ie, afa, amf_espace,
                            bot, cbb, centralbank, eservices, fma
                            )
from core.blacklist import (cbr_unlicensing, cbr_warninglist, govkz_bannedbanks, govkz_banned_fin_organizations,
                            govkz_refund_organizations, govkz_bannedbanks_2level, govkz_unfairactivity_organization,
                            govkz_new_reestr, consob, sca, amf, sfc, fsa, asc,
                            fma_govt_nz_scams, osc, nssmc_ua, moneysmart_au, fsma, fca_uk, centralbank_ie,
                            sec_gov, mas_sg, cssf_lu, sec_ph
                            )


class Parsers:
    WINDOW_BETWEEN_MESSAGES_SECONDS = 60 * 60 * 12
    WINDOW_BETWEEN_SOURCES_SECONDS = 60
    data_units_load_counter = 0
    parsers_data: list[str, int] = []
    ONE_PARSER_MSG = '''🌐 {0} - [<strong>{1}</strong>] \n'''
    SUCCESS_PARSERS_LOG_MSG = '''{0}\n🔚 Amount of dataunits - <b>{1}</b>
    '''

    def publisher(self, func: callable, source_name: str) -> None:
        # try:
        parsers_load_counter = 0

        # self.write_log_and_send_to_telegram(f"ETL process with source <{source_name}> has been started")
        logging.info(f"ETL process with source <{source_name}> has been started")

        connection = pika.BlockingConnection(pika.ConnectionParameters('localhost'))
        channel = connection.channel()
        channel.queue_declare(queue='ETL', durable=True)

        for data_unit in func:
            logging.info(data_unit)
            channel.basic_publish(exchange='', routing_key='ETL', body=data_unit)
            self.data_units_load_counter += 1
            parsers_load_counter += 1

        self.parsers_data.append([source_name, parsers_load_counter])
        # self.write_log_and_send_to_telegram(
        logging.info(
            f"ETL process with source <{source_name}> has been finished. The amount of data in "
            f"this parser is {parsers_load_counter}. Amount of dataunits for parsing session "
            f"(this parser and before them): {self.data_units_load_counter}")

        parsers_load_counter = None
        time.sleep(self.WINDOW_BETWEEN_SOURCES_SECONDS)
        # except Exception as e:
        #     self.parsers_data.append([source_name, -1])
        #     self.write_log_and_send_to_telegram(f"Current resource was stopped cause of global error: {e}",
        #                                         'error')
        # finally:
        if 'connection' in locals():
            connection.close()

    def start_parsing(self) -> None:
        self.write_log_and_send_to_telegram(f"Loop of scraping has been started {datetime.now()}")

        for parser in self.list_of_parsers():
            self.publisher(parser[0], parser[1])

        self.logging_for_tg(self.parsers_data, self.data_units_load_counter)
        self.write_log_and_send_to_telegram(f"Loop of scraping has been finished {datetime.now()}")

    @staticmethod
    def list_of_parsers() -> list[Union[list[Union[BaseDataUnit, str]], Any]]:
        return [
            [bafin.data_unit_iterator(), "Белый список.Корпоративная база данных BaFin"],  # 0
            [consob.data_unit_iterator(), "Черный список. Список предупреждений Италии"],  # 1
            [sca.data_unit_iterator(), "Черный список. Список предупреждений для инвесторов ОАЭ"],  # 2
            [amf.data_unit_iterator(), "Черные списки неавторизованных компаний и сайтов Франции"],  # 3
            [sfc.data_unit_iterator(), "Черный список. Cписок организаций, неодобренных SFC"],  # 4
            [fsa.data_unit_iterator(),  # 5
             "Черный список. Список лиц, занимающихся торговлей финансовыми инструментами без регистрации в Японии"],
            [asc.data_unit_iterator(), "Черный список. Инвестиционный список предостережения Канады"],  # 6
            [scm.data_unit_iterator(), "Черный список. Список предупреждений для инвесторов Малайзии"],  # 7
            [national_bank_kz.data_unit_iterator(), "Белый список.Национальный банк РК"],  # 8
            [cbr_forex.data_unit_iterator(), "ЦБ РФ Список форекс-дилеров"],  # 9
            [cbr_reestersavers.data_unit_iterator(), "ЦБ РФ Список регистраторов"],  # 10
            [cbr_trust.data_unit_iterator(), "ЦБ РФ Список доверительных управляющих"],  # 11
            [cbr_dealers.data_unit_iterator(), "ЦБ РФ Список дилеров"],  # 12
            [cbr_depositaries.data_unit_iterator(), "ЦБ РФ Список депозитариев"],  # 13
            [cbr_brokers.data_unit_iterator(), "ЦБ РФ Список брокеров"],  # 14
            [cbr_specdepositaries.data_unit_iterator(),  # 15
             "ЦБ РФ Реестр лицензий специализированных депозитариев инвестиционных фондов, паевых инвестиционных фондов и негосударственных пенсионных фондов"],
            [cbr_advisors.data_unit_iterator(), "ЦБ РФ Единый реестр инвестиционных советников"],  # 16
            [govkz_securities_transactions.data_unit_iterator(),  # 17
             "GOV KZ Реестр выданных, переоформленных лицензий на проведение банковских и иных операций и осуществление деятельности на рынке ценных бумаг"],
            [govkz_individual_banking_transactions.data_unit_iterator(),  # 18
             "GOV KZ Реестр выданных, переоформленных лицензий на осуществление отдельных видов банковских операций"],
            [govkz_bannedbanks.data_unit_iterator(),  # 19
             "GOV KZ РЕЕСТР ПРИОСТАНОВЛЕННЫХ, ЛИБО ПРЕКРАТИВШИХ ДЕЙСТВИЕ (ЛИШЕННЫХ) ЛИЦЕНЗИЙ НА ПРОВЕДЕНИЕ БАНКОВСКИХ И ИНЫХ ОПЕРАЦИЙ, ОСУЩЕСТВЛЯЕМЫХ БАНКАМИ"],
            [govkz_banned_fin_organizations.data_unit_iterator(),  # 20
             "GOV KZ Реестр приостановленных, либо прекративших действие (лишенных) лицензий на осуществление отдельных видов банковских операций"],
            [govkz_refund_organizations.data_unit_iterator(),  # 21
             "GOV KZ Реестр прекративших действие лицензий организаций, осуществлявших отдельные виды банковских операций в связи с добровольным возвратом."],
            [govkz_bannedbanks_2level.data_unit_iterator(),  # 22
             "GOV KZ Реестр прекративших действие лицензий банков второго уровня в связи с добровольным возвратом"],
            [govkz_unfairactivity_organization.data_unit_iterator(),
             "GOV KZ Список организаций, имеющих признаки недобросовестной деятельности"],  # 23
            [cbr_unlicensing.data_unit_iterator(),
             "ЦБ РФ Реестр аннулированных лицензий профессиональных участников рынка ценных бумаг"],  # 24
            [cbr_warninglist.data_unit_iterator(),
             "ЦБ РФ Список компаний с выявленными признаками нелегальной деятельности на финансовом рынке"],  # 25
            [govkz_new_reestr.data_unit_iterator(), "Реестр финансовых пирамид"],  # 26
            [fma_govt_nz_business.data_unit_iterator(), "FMA Лицензированные и подотчетные лица"],  # 27
            [fma_govt_nz_scams.data_unit_iterator(), "FMA Предупреждения и оповещения"],  # 28
            [finanssivalvonta.data_unit_iterator(), "Реестр утвержденных ценных бумаг Финляндия"],  # 29
            [registers_centralbank_ie.data_unit_iterator(), "Реестр поставщиков финансовых услуг"],  # 30
            [osc.data_unit_iterator(), "Предупреждения и оповещения инвесторов Канады"],  # 31
            [afa.data_unit_iterator(), "Реестр уполномоченных лиц Андорры"],  # 32
            [amf_espace.data_unit_iterator(), "Белый список. Реестр поставщиков инвестиционных услуг Франции"],  # 33
            [nssmc_ua.data_unit_iterator(), "Реестр защиты украинских инвесторов"],  # 34
            [moneysmart_au.data_unit_iterator(), "Черный список. Список предупреждений для инвесторов Австралии"],  # 35
            [fsma.data_unit_iterator(), "Черный список. Список компаний, незаконно действующих в Бельгии"],  # 36
            [fca_uk.data_unit_iterator(), "Черынй список.Список предупреждений FCA о неавторизованных фирмах UK"],  # 37
            [bot.data_unit_iterator(), "Белый список.Реестр лицензированных поставщиков Тайланда"],  # 38
            [cbb.data_unit_iterator(), "CBB. Белый список. Бахрейн"],  # 39
            [centralbank.data_unit_iterator(), "Centralbank"],  # 40
            [eservices.data_unit_iterator(), "Реест подтвержденных финансовых учереждений Сингапура"],  # 41
            [fma.data_unit_iterator(), "Финансовый надзор Австрии"],  # 42
            [centralbank_ie.data_unit_iterator(), "Список неавторизованных фирм Ирландии"],  # 43
            [sec_gov.data_unit_iterator(), "Черный список.Предупреждение о незарегистрированных организациях"],  # 44
            [mas_sg.data_unit_iterator(), "Черный список. Список предупреждений для инвесторов Сингапура"],  # 45
            [cssf_lu.data_unit_iterator(), "Черный список. Список предупреждений Люксембурга"],  # 46
            [sec_ph.data_unit_iterator(), "Черный список. Список предупреждений для инвесторов Филиппинов"],  # 47
        ]

    @staticmethod
    def write_log_and_send_to_telegram(text: str, type_of_log: str = 'info') -> None:
        if type_of_log == 'info':
            logging.info(text)
            tg_bot.send_message(env['CHAT_FOR_SUCCESS_LOGS'], text)
        if type_of_log == 'error':
            logging.error(text)
            tg_bot.send_message(env['CHAT_FOR_ERROR_LOGS'], text)

    def logging_for_tg(self, data_units: list[str, int], amount: int):
        parsers_msg = ''
        for d_u in data_units:
            parsers_msg += self.ONE_PARSER_MSG.format(d_u[0], str(d_u[1]))

        sending_message = self.SUCCESS_PARSERS_LOG_MSG.format(parsers_msg, str(amount))
        tg_bot.send_message(env['CHAT_FOR_SUCCESS_LOGS'], sending_message, parse_mode='html')
