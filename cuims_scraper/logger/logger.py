import logging



logging.basicConfig(level=logging.INFO, filename='scraper.log',
                    filemode='w', format="%(asctime)s -> %(levelname)s: %(message)s")


def log_info(x=''):
    logging.info(x)

def log_debug(x=''):
    logging.debug(x)

def log_error(x=''):
    logging.error(x)

def log_warning(x=''):
    logging.warning(x)

def log_critical(x=''):
    logging.critical(x)

def log_exception(x=''):
    logging.exception(x)