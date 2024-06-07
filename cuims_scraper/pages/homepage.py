import os
from shutil import move

from ..logger import *
from ..startup import StaleElementReferenceException
from ..startup import NoSuchElementException
from ..startup import PdfReader
from ..startup import By
from ..startup import wait_for_loader



def get_homepage(driver, dictionary, download_path='', get_IDcard=True) -> list:

    if get_IDcard and download_path == '':
        error("You must enter your downloading path if you want to retrive the ID card.")
        return

    info("Moving to the home page.")
    try:
        # move to the home page
        page = driver.find_element(By.ID, 'aHome')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        #

        # get mentor details
        info("Getting mentor details.")
        itr = 0
        while True:
            try:
                list_items = driver.find_element(By.ID, 'divStudentMentorDetails')
                list_items = list_items.find_elements(By.TAG_NAME, "li")
                name = ''.join(list_items[0].text.split(' ')[2:])
                email = ''.join(list_items[1].text.split(' ')[2:])
                dictionary['mentor'] = {'name': name, 'email': email}
                info("Mentor details recived successfully.")
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
                dictionary['mentor'] = None
                exception("Mentor details couldn't be recived.")
                break
        # 

        # get important messages
        info("Getting messages.")
        itr = 0
        while True:
            try:
                messages = driver.find_element(By.ID, 'divStudentMyMessages').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
                dictionary['messages'] = list({mess.text for mess in messages})
                info("Messages recived successfully.")
                break
            except StaleElementReferenceException:
                pass
            except NoSuchElementException as e:
                itr += 1
                if itr == 50:
                    raise e
                else:
                    pass
            except:
                dictionary['messages'] = None
                exception("Messages couldn't be recived.")
                break
        # 

        # download and move ID card to working directory
        if get_IDcard:
            info("Getting ID card.")
            try:

                driver.find_element(By.ID, 'div_virtual_idcard').find_element(By.TAG_NAME, 'a').click()
                info("Downloading ID card.")
                try:
                    found = False
                    itr = 0
                    while not found:
                        itr += 1
                        if itr == 50:
                            error("ID card couldn't be downloaded. Most likely the downlod button didn't get pressed or internet speed is super slow.")
                            break
                        else:
                            pass
                        for filename in os.listdir(download_path):
                            if filename.startswith('Virtual_ID_Card_'):
                                source_path = os.path.join(download_path, filename)
                                destination_path = os.path.join(os.getcwd(), f'{dictionary['UID']}_ID.pdf')
                                try:
                                    with open(source_path, 'rb') as pdf_file:
                                        PdfReader(pdf_file) # If file is empty it raises an error
                                        info("ID card downloaded.")
                                        try:
                                            os.remove(f'{dictionary['UID']}_ID.pdf')
                                            info("Previous ID card removed.")
                                        except:
                                            pass
                                        move(source_path, destination_path)
                                        info("ID card recived successfully.")
                                        driver.switch_to.window(driver.window_handles[0])
                                        found = True
                                except:
                                    exception("ID card didn't download properly.")
                except:
                    try:
                        os.listdir(download_path)
                        exception(f"Directory ({download_path}) doesn't seem to be your download directory.")
                    except:
                        exception(f"The directory {download_path} doesn't exist in your system.")
            except:
                exception("ID card couldn't be downloaded.")
            #
        return [dictionary['messages'], dictionary['mentor']]

    except:
        exception("Couldn't navigate to home page.")
        dictionary['messages'] = None
        dictionary['mentor'] = None
        return None
    # 
