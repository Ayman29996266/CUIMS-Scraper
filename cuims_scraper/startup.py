try:
    from selenium.common.exceptions import ElementNotInteractableException
    from selenium.common.exceptions import StaleElementReferenceException
    from selenium.common.exceptions import NoSuchElementException
    from selenium.common.exceptions import TimeoutException
    from selenium.webdriver import FirefoxOptions
    from selenium.webdriver import Firefox
    from selenium.webdriver.common.by import By
except:
    print("You need to have selenium package installed to use cuims_scraper.")
    exit(1)

try:
    from PyPDF2 import PdfReader
except:
    print("You need to have PyPDF2 package installed to use cuims_scraper.")
    exit(1)

try:
    from PIL import Image
except:
    print("You need to have PIL package installed to use cuims_scraper.")
    exit(1)

try:
    import easyocr
except:
    print("You need to have easyocr package installed to use cuims_scraper.")
    exit(1)


def wait_for_loader(driver) -> None:
    try:
        while True:
            driver.find_element(By.ID, "loader-wrapper").click()
    except:
        return
