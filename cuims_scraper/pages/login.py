from inspect import currentframe
from inspect import getfile

from ..logger import *
from ..startup import ElementNotInteractableException
from ..startup import StaleElementReferenceException
from ..startup import easyocr
from ..startup import Image
from ..startup import By



def get_captcha(driver) -> str:
    path = getfile(currentframe())[:-8] + "captcha.png"
    driver.get_screenshot_as_file(path)

    img = Image.open(path)
    box = (390, 470, 460, 510)
    cropped = img.crop(box=box)
    cropped.save(path)

    reader = easyocr.Reader(['en'])
    cap = reader.readtext(path)[0][1]

    return cap



def login(driver, UID, PASSWORD) -> None:
    info("Logging in...")

    info("Locating, filling and posting UID form...")
    try:
        UID_input = driver.find_element(By.ID, 'txtUserId')
        UID_input.click()
        UID_input.send_keys(UID)
        next_btn = driver.find_element(By.ID, 'btnNext')
        next_btn.click()
        info("Done.")
    except:
        exception("Couldn't post UID form.")
    
    
    while True:
        info("Locating, filling and posting password and captcha...")
        try:
            pass_input = driver.find_element(By.ID, 'txtLoginPassword')
            pass_input.click()
            pass_input.send_keys(PASSWORD)
            info("Password done.")
        except:
            exception("Couldn't fill password ")
            continue

        info("Getting captcha input from user")
        try:
            cap_input = driver.find_element(By.ID, 'txtcaptcha')
            cap_input.click()
            cap_input.clear()
            cap_input.send_keys(get_captcha(driver))
        except:
            exception("Couldn't fill captcha.")
            continue

        try:
            driver.find_element(By.ID, 'btnLogin').click()
        except:
            exception("Couldn't log in.")

        while True:
            try:
                driver.implicitly_wait(1)
                text = driver.find_elements(By.TAG_NAME, "p")[1].text.split(' ')[0]
                assert text == 'Forgot'
                driver.find_element(By.CSS_SELECTOR, "button[class='confirm']").click()
                error("Wrong captcha. Redo...")
                break
            except ElementNotInteractableException:
                pass
            except StaleElementReferenceException:
                pass
            except AssertionError:
                info(f"Loged in successfully as {UID}")
                driver.implicitly_wait(10)
                return
            except:
                critical("Couldn't login properly..")
                exception()
                exit(1)
                
            