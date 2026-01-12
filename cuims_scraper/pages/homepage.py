import os
import time
from shutil import move
from typing import Any, Dict, List, Optional, Tuple, Callable

from PyPDF2 import PdfReader
from PyPDF2.errors import PdfReadError

from selenium.common.exceptions import (
    TimeoutException,
    NoSuchElementException,
    StaleElementReferenceException,
)
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

from ..shared import wait_for_loader
from ..logger import log_info, log_warning, log_error, log_critical, log_exception
from ..constants import (
    ID_DOWNLOAD_BTN_ID,
    HOME_PAGE_BTN_ID,
    MENTOR_LIST_ID,
    MESSAGES_LIST_ID,
)


def _wait_for_firefox_download(
    download_dir: str,
    start_download: Callable[[], None],
    timeout: int = 60,
    poll_interval: float = 0.25,
    filename_contains: Optional[str] = None,
) -> str:
    """
    Wait for a file download to finish in Firefox.

    Strategy:
    1) Snapshot directory before click.
    2) Click.
    3) Watch for ANY new file(s), including *.part.
    4) Wait until no *.part remain and a candidate file is size-stable.
    """
    download_dir = os.path.abspath(download_dir)
    if not os.path.isdir(download_dir):
        raise FileNotFoundError(f"Download directory does not exist: {download_dir}")

    before = set(os.listdir(download_dir))
    start_download()
    deadline = time.time() + timeout

    seen_new: set[str] = set()

    while time.time() < deadline:
        now = set(os.listdir(download_dir))
        new_names_all = list(now - before)

        if filename_contains:
            new_names_all = [n for n in new_names_all if filename_contains in n]

        if new_names_all:
            seen_new.update(new_names_all)

            # If any partials exist among the new files, keep waiting
            # (Firefox uses .part while download is in progress).
            if any(n.endswith(".part") for n in seen_new):
                time.sleep(poll_interval)
                continue

            # Consider only non-.part new files as final candidates
            candidates = [n for n in seen_new if not n.endswith(".part")]
            if not candidates:
                time.sleep(poll_interval)
                continue

            candidate_path = max(
                (os.path.join(download_dir, n) for n in candidates),
                key=os.path.getmtime,
            )

            # Size-stable check
            try:
                s1 = os.path.getsize(candidate_path)
                time.sleep(poll_interval)
                s2 = os.path.getsize(candidate_path)
            except FileNotFoundError:
                time.sleep(poll_interval)
                continue

            if s1 == s2 and s2 > 0:
                return os.path.abspath(candidate_path)

        time.sleep(poll_interval)

    raise TimeoutException(
        f"Timed out waiting for Firefox download in '{download_dir}'."
    )


def _download_and_move_id_card(
    driver,
    uid: str,
    download_timeout: int = 60,
    out_dir: Optional[str] = None,
) -> Optional[str]:
    """
    Download the ID card PDF and move it into out_dir.

    Assumption: Firefox download directory == CWD.
    """
    download_dir = os.path.abspath(os.getcwd())  # enforce CWD
    out_dir = os.path.abspath(out_dir or os.getcwd())
    dest_path = os.path.join(out_dir, f"{uid}_ID.pdf")

    btn_div = driver.find_element(By.ID, ID_DOWNLOAD_BTN_ID)
    btn_anchor = btn_div.find_element(By.TAG_NAME, "a")

    source_path = _wait_for_firefox_download(
        download_dir=download_dir,
        start_download=btn_anchor.click,
        timeout=download_timeout,
        filename_contains=None,
    )

    # Validate PDF (some sites download HTML error pages / empty PDFs)
    try:
        with open(source_path, "rb") as f:
            PdfReader(f)
    except PdfReadError:
        log_exception("Downloaded ID card is not a readable PDF (corrupt/empty).")
        return None

    # Replace any existing output file
    try:
        if os.path.exists(dest_path):
            os.remove(dest_path)
            log_info("Previous ID card removed.")
    except OSError:
        log_warning("Could not remove previous ID card; will attempt to overwrite by move.")

    move(source_path, dest_path)
    return dest_path


def get_homepage(
    driver,
    dictionary: Dict[str, Any],
    download_id_file: bool = True,
) -> Optional[Tuple[Optional[List[str]], Optional[Dict[str, str]]]]:
    """
    Collect homepage data (mentor info, messages) and optionally download the ID card.

    Note: download path is assumed to be CWD.
    """

    log_info("Moving to the home page.")
    wait = WebDriverWait(driver, 10)

    try:
        wait.until(EC.presence_of_element_located((By.ID, HOME_PAGE_BTN_ID)))
    except TimeoutException:
        log_critical("Home page marker not found after login (timeout).")
        raise

    wait_for_loader(driver)

    mentor: Optional[Dict[str, str]] = None
    try:
        log_info("Getting mentor details.")
        mentor_ul = wait.until(EC.presence_of_element_located((By.ID, MENTOR_LIST_ID)))
        items = WebDriverWait(mentor_ul, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "li"))
        )
        mentor = {"name": items[0].text.strip(), "email": items[1].text.strip()}
        log_info("Mentor details received successfully.")
    except (
        TimeoutException,
        NoSuchElementException,
        IndexError,
        StaleElementReferenceException,
    ):
        log_warning("Was not able to get mentor details. Skipping.")
        log_exception()

    dictionary["mentor"] = mentor

    messages: Optional[List[str]] = None
    try:
        log_info("Getting messages.")
        msg_list = wait.until(EC.presence_of_element_located((By.ID, MESSAGES_LIST_ID)))
        spans = WebDriverWait(msg_list, 10).until(
            EC.presence_of_all_elements_located((By.TAG_NAME, "span"))
        )
        messages = sorted({s.text.strip() for s in spans if s.text and s.text.strip()})
        log_info("Messages received successfully.")
    except (TimeoutException, NoSuchElementException, StaleElementReferenceException):
        log_warning("Was not able to get important messages. Skipping.")
        log_exception()

    dictionary["messages"] = messages

    if download_id_file:
        uid = str(dictionary.get("UID", "")).strip()
        if not uid:
            log_error(
                "dictionary does not contain 'UID' and download_id_file is set to True."
            )
        else:
            try:
                log_info("Downloading ID card.")
                downloaded = _download_and_move_id_card(driver=driver, uid=uid)
                if downloaded:
                    log_info(f"ID card downloaded successfully: {downloaded}")
                else:
                    log_warning("ID card download/validation failed.")
            except (TimeoutException, NoSuchElementException, FileNotFoundError):
                log_exception("ID card couldn't be downloaded/moved.")

    return messages, mentor
