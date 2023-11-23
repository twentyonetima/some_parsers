import logging

from main import Parsers

logging.basicConfig(
    filename='ETL.log',
    encoding='utf-8',
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%m/%d/%Y %I:%M:%S %p')

parsers = Parsers()

parsers.start_parsing()
