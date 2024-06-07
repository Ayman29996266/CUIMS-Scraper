import logging



logging.basicConfig(level=logging.INFO, filename='scraper.log',
                    filemode='w', format="%(asctime)s -> %(levelname)s: %(message)s")


def info(x=''):
    logging.info(x)

def debug(x=''):
    logging.debug(x)

def error(x=''):
    logging.error(x)

def warning(x=''):
    logging.warning(x)

def critical(x=''):
    logging.critical(x)

def exception(x=''):
    logging.exception(x)