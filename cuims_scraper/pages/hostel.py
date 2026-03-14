from __future__ import annotations

from typing import Any, Dict

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, WebDriverException

from ..logger import log_info, log_exception, log_warning
from ..constants import (
    HOSTEL_DETAILS_ID,
    BURGER_MENU_BTN_CLASS,
    HOSTEL_PAGE_NAV_BTN_CSS_SELECTOR,
)


def get_hostel(driver, dictionary: Dict[str, Any], timeout: int = 10) -> None:
    """
    Populate dictionary["hostel"] with hostel details.

    On success:
      dictionary["hostel"] = {<th text>: <td text>, ...}

    On failure (navigation/scrape issues):
      dictionary["hostel"] = None
    """
    dictionary["hostel"] = None

    log_info("Moving to hostel page.")
    wait = WebDriverWait(driver, timeout)

    menu = wait.until(
        EC.element_to_be_clickable((By.CLASS_NAME, BURGER_MENU_BTN_CLASS))
    )
    menu.click()

    details_btn = wait.until(
        EC.presence_of_element_located((By.CSS_SELECTOR, HOSTEL_PAGE_NAV_BTN_CSS_SELECTOR))
    )
    ul_id = details_btn.parent.parent.id
    hostel_li = wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, f"li[data-target*='#{ul_id}']"))
    )
    hostel_a = WebDriverWait(hostel_li, 10).until(
        EC.element_to_be_clickable((By.TAG_NAME, "a"))
    )
    hostel_a.click()
    wait.until(
        EC.element_to_be_clickable((By.CSS_SELECTOR, HOSTEL_PAGE_NAV_BTN_CSS_SELECTOR))
    )
    details_btn.click()

    try:
        # Prefer visible over merely present when the goal is to read text reliably.
        details = wait.until(
            EC.visibility_of_element_located((By.ID, HOSTEL_DETAILS_ID))
        )
        log_info("Getting hostel details")

        rows = details.find_elements(By.TAG_NAME, "tr")
        if not rows:
            log_warning("No hostel details found.")
            return

        hostel: Dict[str, str] = {}
        for row in rows:
            headers = row.find_elements(By.TAG_NAME, "th")
            cells = row.find_elements(By.TAG_NAME, "td")
            if not headers or not cells:
                continue

            key = headers[0].text.strip()
            value = cells[0].text.strip()
            if key:
                hostel[key] = value

        dictionary["hostel"] = hostel or None
        log_info("Hostel details received successfully.")

    except TimeoutException:
        log_exception(
            "Couldn't navigate to the hostel page (timeout waiting for details container)."
        )
    except WebDriverException:
        log_exception("Couldn't receive hostel details due to a WebDriver error.")
