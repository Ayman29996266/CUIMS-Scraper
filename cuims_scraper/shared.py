from .constants import LOADER_WRAPPER_ID
from .logger.logger import log_critical

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException
from selenium.webdriver.support import expected_conditions as EC

class UnknownException(Exception):
    pass

class CredentialsError(Exception):
    pass

def wait_for_loader(driver) -> None:
    try:
        WebDriverWait(driver, 10).until(EC.invisibility_of_element((By.ID, LOADER_WRAPPER_ID)))
    except TimeoutException:
        log_critical("Timed-out waiting for the loader wrapper. Exiting...")
        raise TimeoutException