from ..constants import *
from ..logger import *

from selenium.common.exceptions import (
    TimeoutException,
    ElementNotInteractableException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO
import easyocr
import numpy as np


def get_captcha(driver, reader, captcha_id: str, timeout: int = 10) -> str:
    """
    Capture the captcha image element and extract its text using EasyOCR.

    Args:
        driver: Selenium WebDriver instance currently on the page that shows the captcha.
        captcha_id: The HTML id attribute of the captcha image element.
        timeout: Seconds to wait for the captcha element to be present.

    Returns:
        The OCR-extracted captcha text (stripped).

    Raises:
        TimeoutException: If the captcha element does not appear within `timeout`.
        IndexError: If OCR returns no results (nothing readable).
    """

    captcha_el = WebDriverWait(driver, timeout).until(
        EC.presence_of_element_located((By.ID, captcha_id))
    )

    # Take a screenshot of the element itself as PNG bytes.
    png_bytes = captcha_el.screenshot_as_png

    # Convert PNG bytes to a PIL Image then a numpy array so it can be fed to OCR.
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    img = np.array(img)
    results = reader.readtext(img, detail=0)

    # detail=0 returns a simple list of strings (best match first).
    try:
        return results[0].strip()
    except IndexError:
        critical("EasyOCR was not able to read the captcha image.")
        return ""


def login(driver, uid: str, password: str, attempts: int = 5) -> None:
    """
    Log into the website using UID, password, and an OCR-scanned captcha (may need retries).

    The function:
    1) Enters the UID and clicks Next.
    2) Repeatedly enters password + scanned captcha and clicks Login.
    3) After each submission, checks whether the login page is still present:
       - If still on login page and an error popup indicates wrong captcha, retry.
       - If error indicates wrong credentials, exits with a credentials error code.
       - If login page is gone, treats it as a successful login.

    Args:
        driver: Selenium WebDriver instance already on the login page.
        uid: User ID to submit.
        password: Password to submit.
        attempts: Maximum number of captcha/login retries before giving up.

    Raises:
        TimeoutException: If required elements never appear within wait time.
    """
    info("Logging in...")

    wait = WebDriverWait(driver, 10)

    # --- Step 1: UID page ---
    info("Entering UID and clicking Next...")
    try:
        uid_field = wait.until(EC.element_to_be_clickable((By.ID, UID_FIELD_ID)))
        uid_field.clear()
        uid_field.send_keys(uid)

        next_btn = wait.until(EC.element_to_be_clickable((By.ID, NEXT_BTN_ID)))
        next_btn.click()
        info("UID submitted.")
    except TimeoutException:
        exception("Couldn't fill and post the UID field (timeout).")
        raise

    # --- Step 2: Password + captcha page ---
    reader = easyocr.Reader(["en"])  # for captcha scan

    info("Entering password + captcha and submitting...")
    for attempt in range(1, attempts + 1):
        info(f"Login attempt {attempt}/{attempts}...")

        try:
            pw_field = wait.until(
                EC.element_to_be_clickable((By.ID, PASSWORD_FIELD_ID))
            )
            pw_field.clear()
            pw_field.send_keys(password)

            cap_field = wait.until(
                EC.element_to_be_clickable((By.ID, CAPTCHA_FIELD_ID))
            )
            cap_field.clear()
            cap_field.send_keys(get_captcha(driver, reader, CAPTCHA_IMAGE_ID))

            login_btn = wait.until(EC.element_to_be_clickable((By.ID, LOGIN_BTN_ID)))
            login_btn.click()
        except TimeoutException:
            exception("Couldn't fill password/captcha or click login (timeout).")
            continue
        except (ElementNotInteractableException, StaleElementReferenceException):
            # DOM updated during interaction; retry the whole attempt.
            continue

        # --- Step 3: Determine success vs. form error ---
        # If login page marker is absent, assume success.
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, LOGIN_PAGE_ID))
            )
        except TimeoutException:
            info("Login successful.")
            return

        # Still on login page: try to detect error popup and decide what to do.
        try:
            popups = driver.find_elements(By.CLASS_NAME, LOGIN_ERROR_POPUP_CLASS)
            if not popups:
                warning("Still on login page, but no error popup found. Retrying...")
                continue

            # Collect all <p> messages in the popup.
            ps = popups[0].find_elements(By.TAG_NAME, "p")
            messages = " ".join(p.text for p in ps)

            if "User" in messages:
                info("Wrong credentials. Exiting...")
                exit(CREDENTIALS_ERROR_EXIT_CODE)
            if "Captcha" in messages:
                info("Wrong captcha. Retry...")
            else:
                warning("Unknown form error. Retry...")

            # Remove the error popup
            error_buttons = driver.find_elements(By.CLASS_NAME, LOGIN_ERROR_BTN_CLASS)
            if error_buttons:
                for btn in error_buttons:
                    btn.click()
            else:
                critical("Error popup detected, but no '.confirm' buttons were found.")
                exit(UNKNOWN_ERROR_EXIT_CODE)

        except (ElementNotInteractableException, StaleElementReferenceException):
            # Popup/button not interactable due to animation/DOM refresh; retry.
            continue
        except Exception:
            critical("Couldn't determine login error state. Exiting...")
            exception()
            exit(UNKNOWN_ERROR_EXIT_CODE)

    critical("Exceeded maximum login attempts. Exiting...")
    exit(TIMEOUT_ATTEMPTS_EXIT_CODE)
