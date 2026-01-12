from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_datesheet(driver, dictionary) -> dict:

    log_info("Moving to date sheet page.")
    try:
        # Move to the date sheet page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudentDatesheet.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        dictionary['date sheet'] = {}
        wait_for_loader(driver)
        #

        # get the date sheet
        log_info("Getting the date sheet.")
        try:
            itr = 0
            while True:
                try:
                    table = driver.find_element(By.CLASS_NAME, 'container-fluid').find_element(By.TAG_NAME, 'table')
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    dictionary['date sheet'] = {
                        rows[0].find_elements(By.TAG_NAME, 'th')[i].text:
                        [rows[j + 1].find_elements(By.TAG_NAME, 'td')[i].text 
                        for j in range(len(rows) - 1)]
                        for i in range(len(rows[0].find_elements(By.TAG_NAME, 'th')))
                    }
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

            log_info("Date sheet recived successfully.")
            return dictionary['date sheet']
        except:
            dictionary['date sheet'] = None
            log_exception("Date sheet couldn't be recived.")
            return dictionary['date sheet']
        #
    except:
        log_exception("Couldn't navigate to the date sheet page.")
        dictionary['date sheet'] = None
        return dictionary['date sheet']
    #