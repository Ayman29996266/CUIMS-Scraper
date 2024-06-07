from io import BytesIO
from base64 import b64decode
from os import remove

from ..logger import *
from ..startup import StaleElementReferenceException
from ..startup import NoSuchElementException
from ..startup import Image
from ..startup import By
from ..startup import wait_for_loader



def get_profile(driver, dictionary, get_profile_pic=True) -> dict:
    info("Moving to profile page.")
    try:
        # Move to the profile page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudentProfile.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        #

        # get profile picture
        if get_profile_pic:
            info("Getting profile picture.")
            itr = 0
            try:
                while True:
                    try:
                        lines = driver.find_elements(By.CLASS_NAME, 'row')
                        profile_pic = lines[0].find_element(By.TAG_NAME, 'img')
                        break
                    except StaleElementReferenceException:
                        pass
                    except NoSuchElementException as e:
                        itr += 1
                        if itr == 50:
                            raise e
                        else:
                            pass
                    except Exception as e:
                        raise e

                src_attribute = profile_pic.get_attribute('src')
                base64_data = src_attribute.split(',')[1]
                decoded_data = b64decode(base64_data)
                image = Image.open(BytesIO(decoded_data))
                try:
                    remove(f'{dictionary['UID']}_profile_pic.png')
                    info("Previous picture removed.")
                except:
                    pass
                image.save(f'{dictionary['UID']}_profile_pic.png')
                info("Picture saved successfully.")
            except:
                try:
                    lines = driver.find_elements(By.CLASS_NAME, 'row')
                    exception("Profile picture couldn't be downloaded.")
                except:
                    exception("No profile information found.")
                    dictionary['profile'] = None
                    return
        # 

        # get profile information
        info("Getting profile information.")
        itr = 0
        while True:
            try:
                lines = driver.find_elements(By.CLASS_NAME, 'row')
                dictionary['profile'] = {
                    lines[i + 1].find_elements(By.TAG_NAME, "div")[0].text:
                    lines[i + 1].find_elements(By.TAG_NAME, 'div')[1].text
                    for i in range(15)
                }
                info("Profile information recived successfully.")
                break
            except NoSuchElementException as e:
                itr += 1
                if itr == 50:
                    raise e
                else:
                    pass
            except:
                exception("Profile information couldn't be recived.")
                dictionary['profile'] = {}
        # 

        # get qualifications
        info("Getting qualifications.")
        itr = 0
        while True:
            try:
                inner_wrapper = driver.find_element(By.CLASS_NAME, 'inner-wrapper')
                table = inner_wrapper.find_elements(By.TAG_NAME, 'table')[0]
                rows = table.find_elements(By.TAG_NAME, 'tr')
                dictionary['profile']['qualifications'] = {
                    rows[0].find_elements(By.TAG_NAME, 'th')[j].text.lower():
                    [rows[i + 1].find_elements(By.TAG_NAME, 'td')[j].text for i in range(len(rows) - 1)]
                    for j in range(len(rows[0].find_elements(By.TAG_NAME, 'th')))
                }
                info("Qualifications recived successfully.")
                break
            except NoSuchElementException as e:
                itr += 1
                if itr == 50:
                    raise e
                else:
                    pass
            except:
                exception("Qualifications couldn't be recived.")
                dictionary['profile']['qualifications'] = None
        # 

        # get contacts
        info("Getting contacts.")
        itr = 0
        while True:
            try:
                inner_wrapper = driver.find_element(By.CLASS_NAME, 'inner-wrapper')
                table = inner_wrapper.find_elements(By.TAG_NAME, 'table')[1]
                rows = table.find_elements(By.TAG_NAME, 'tr')
                dictionary['profile']['contacts'] = {
                    rows[0].find_elements(By.TAG_NAME, 'th')[j].text.lower():
                    [rows[i + 1].find_elements(By.TAG_NAME, 'td')[j].text for i in range(len(rows) - 1)]
                    for j in range(len(rows[0].find_elements(By.TAG_NAME, 'th')))
                }
                info("Contacts recived successfully")
                break
            except NoSuchElementException as e:
                itr += 1
                if itr == 50:
                    raise e
                else:
                    pass
            except:
                exception("Contacts couldn't be recived.")
                dictionary['profile']['contacts'] = None
        # 

        return dictionary['profile']

    except:
        exception("Couldn't navigate to the profile page.")
        dictionary['profile'] = None
        return dictionary['profile']
    #
