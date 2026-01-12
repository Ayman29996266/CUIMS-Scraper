from __future__ import annotations

from selenium.common.exceptions import (
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from ...constants import (
    UID_FIELD_ID,
    NEXT_BTN_ID,
    PASSWORD_FIELD_ID,
    CAPTCHA_FIELD_ID,
    CAPTCHA_IMAGE_ID,
    LOGIN_BTN_ID,
    LOGIN_PAGE_ID,
    LOGIN_ERROR_BTN_CLASS,
    LOGIN_ERROR_POPUP_CLASS,
)
from .read_captcha import read_captcha
from ...logger import log_info, log_warning, log_critical, log_exception
from ...shared import UnknownException, CredentialsError


def login(driver: WebDriver, uid: str, password: str, *, attempts: int = 5) -> None:
    """
    Log into the website using UID, password, and an OCR-scanned CAPTCHA.

    Workflow:
    1) Fill UID and click "Next".
    2) On password+captcha page: fill password, OCR captcha, submit.
    3) If still on login page, read any error popup and decide:
       - credentials error -> raise CredentialsError
       - captcha error -> retry
       - unknown error -> retry (or raise UnknownException if UI is inconsistent)

    Args:
        driver: Selenium WebDriver.
        uid: User ID for login.
        password: Password for login.
        attempts: Maximum number of captcha retries.

    Raises:
        CredentialsError: If the site indicates the UID/password are wrong.
        UnknownException: If an error popup exists but cannot be dismissed safely.
        TimeoutException: If timeouts occur repeatedly or attempts are exhausted.
    """
    log_info("Logging in...")
    wait = WebDriverWait(driver, 10)

    # --- Step 1: UID page ---
    log_info("Entering UID and clicking Next...")
    try:
        uid_field: WebElement = wait.until(
            EC.element_to_be_clickable((By.ID, UID_FIELD_ID))
        )
        uid_field.clear()
        uid_field.send_keys(uid)

        next_btn: WebElement = wait.until(
            EC.element_to_be_clickable((By.ID, NEXT_BTN_ID))
        )
        next_btn.click()
        log_info("UID submitted.")
    except TimeoutException:
        log_exception("Couldn't fill and post the UID field (timeout).")
        raise

    # --- Step 2: Password + captcha page ---
    log_info("Entering password + captcha and submitting...")
    for attempt in range(1, attempts + 1):
        log_info(f"Login attempt {attempt}/{attempts}...")

        try:
            pw_field: WebElement = wait.until(
                EC.element_to_be_clickable((By.ID, PASSWORD_FIELD_ID))
            )
            pw_field.clear()
            pw_field.send_keys(password)

            cap_field: WebElement = wait.until(
                EC.element_to_be_clickable((By.ID, CAPTCHA_FIELD_ID))
            )
            cap_field.clear()
            cap_field.send_keys(read_captcha(driver, CAPTCHA_IMAGE_ID))

            login_btn: WebElement = wait.until(
                EC.element_to_be_clickable((By.ID, LOGIN_BTN_ID))
            )
            login_btn.click()
        except TimeoutException:
            log_exception("Couldn't fill password/captcha or click login (timeout).")
            continue
        except (ElementNotInteractableException, StaleElementReferenceException):
            continue

        # --- Step 3: Determine success vs. form error ---
        # If the login page id is NOT found quickly, assume navigation occurred -> success.
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, LOGIN_PAGE_ID))
            )
        except TimeoutException:
            log_info("Login successful.")
            return

        # Still on login page: detect error popup and decide what to do.
        try:
            popups: list[WebElement] = driver.find_elements(
                By.CLASS_NAME, LOGIN_ERROR_POPUP_CLASS
            )
            if not popups:
                log_warning(
                    "Still on login page, but no error popup found. Retrying..."
                )
                continue

            paragraphs = popups[0].find_elements(By.TAG_NAME, "p")
            messages = " ".join(p.text for p in paragraphs)

            if "User" in messages:
                log_info("Wrong credentials. Exiting...")
                raise CredentialsError
            if "Captcha" in messages:
                log_info("Wrong captcha. Retry...")
            else:
                log_warning("Unknown form error. Retry...")

            error_buttons: list[WebElement] = driver.find_elements(
                By.CLASS_NAME, LOGIN_ERROR_BTN_CLASS
            )
            if error_buttons:
                for btn in error_buttons:
                    btn.click()
            else:
                log_critical(
                    "Error popup detected, but no '.confirm' buttons were found."
                )
                raise UnknownException

        except (ElementNotInteractableException, StaleElementReferenceException):
            continue

    log_critical("Exceeded maximum login attempts. Exiting...")
    raise TimeoutException
