import shutil
from dataclasses import dataclass
from io import BytesIO
from pathlib import Path
from typing import Optional, Union, Final

from PIL import Image, ImageOps
import pytesseract

from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.remote.webelement import WebElement
from selenium.webdriver.support import expected_conditions as EC

from ...logger import log_critical


PathLike = Union[str, Path]


@dataclass(frozen=True, slots=True)
class TesseractConfig:
    """Runtime configuration for Tesseract OCR."""

    tessdata_dir: Path
    tesseract_cmd: str
    tessdata_config_fragment: str


def _configure_tesseract(
    tessdata_dir: PathLike, tesseract_cmd: Optional[str] = None
) -> TesseractConfig:
    """
    Validate and configure pytesseract to use the system Tesseract binary and a specific tessdata directory.

    Args:
        tessdata_dir: Directory containing language data (*.traineddata), typically shipped with the project.
        tesseract_cmd: Optional explicit path to the `tesseract` executable. If not provided, PATH is searched.

    Returns:
        A `TesseractConfig` object with paths and a reusable config fragment for `image_to_string()`.

    Raises:
        FileNotFoundError: If tessdata_dir is missing or if the tesseract binary cannot be found.
    """
    resolved_tessdata = Path(tessdata_dir).resolve()

    if not resolved_tessdata.is_dir():
        raise FileNotFoundError(f"tessdata directory not found: {resolved_tessdata}")

    cmd = tesseract_cmd or shutil.which("tesseract")
    if not cmd:
        raise FileNotFoundError(
            "tesseract executable not found on PATH. Install Tesseract or pass an explicit path via tesseract_cmd."
        )

    # pytesseract needs to know the binary path (especially on Windows installs).
    pytesseract.pytesseract.tesseract_cmd = cmd

    # Using --tessdata-dir avoids reliance on TESSDATA_PREFIX and OS-specific install paths.
    fragment = f'--tessdata-dir "{resolved_tessdata.as_posix()}"'

    return TesseractConfig(
        tessdata_dir=resolved_tessdata,
        tesseract_cmd=cmd,
        tessdata_config_fragment=fragment,
    )


def _preprocess_captcha(image: Image.Image) -> Image.Image:
    """
    Apply light preprocessing that often improves OCR on CAPTCHA-like images.

    Steps:
    - Convert to grayscale
    - Invert
    - Apply a simple threshold (binarize)

    Args:
        image: PIL image.

    Returns:
        A processed PIL image suitable for OCR.
    """
    img = ImageOps.grayscale(image)
    img = ImageOps.invert(img)

    threshold: Final[int] = 160
    lut = [0 if i <= threshold else 255 for i in range(256)]
    return img.point(lut)


def read_captcha(
    driver: WebDriver,
    captcha_image_id: str,
    *,
    timeout_s: int = 10,
    tesseract: Optional[TesseractConfig] = None,
) -> str:
    """
    Capture a CAPTCHA image element screenshot and OCR it using Tesseract.

    Args:
        driver: Selenium WebDriver instance controlling the browser.
        captcha_image_id: DOM id of the CAPTCHA <img> (or screenshot-able element).
        timeout_s: Seconds to wait for the CAPTCHA element to exist in the DOM.
        tesseract: Optional preconfigured `TesseractConfig`. If not provided, a project-local
            '.traineddata' file next to this file is assumed.

    Returns:
        OCR'd text (may be empty if OCR fails).
    """
    captcha_el: WebElement = WebDriverWait(driver, timeout_s).until(
        EC.presence_of_element_located((By.ID, captcha_image_id))
    )

    if tesseract is None:
        default_tessdata = Path(__file__).resolve().parent
        tesseract = _configure_tesseract(default_tessdata)

    png_bytes: bytes = captcha_el.screenshot_as_png
    img = Image.open(BytesIO(png_bytes)).convert("RGB")
    img = _preprocess_captcha(img)

    # --psm 7: treat image as a single text line (often reasonable for captchas).
    # --oem 3: default engine mode.
    config = f"{tesseract.tessdata_config_fragment} --oem 3 --psm 7 -l eng"
    text: str = pytesseract.image_to_string(img, config=config)

    if not text:
        log_critical("Tesseract was not able to read the captcha image.")
    return text.strip()

