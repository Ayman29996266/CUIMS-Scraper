from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_prac_datesheet(driver, dictionary) -> dict:

    info("Moving to practical date sheet page.")
    try:
        # Move to the practical date sheet page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudentPracticleDateSheet.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        dictionary['practical date sheet'] = {}
        #

        # get the practical date sheet
        info("Getting the practical date sheet.")
        try:
            itr = 0
            while True:
                try:
                    table = driver.find_element(By.ID, 'divScrollBar').find_element(By.TAG_NAME, 'table')
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    dictionary['practical date sheet'] = {
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

            info("Practical date sheet recived successfully.")
            return dictionary['practical date sheet']
        except:
            dictionary['Practical date sheet'] = None
            exception("Practical date sheet couldn't be recived.")
            return dictionary['practical date sheet']
        #
    except:
        exception("Couldn't navigate to the practical date sheet page.")
        dictionary['practical date sheet'] = None
        return dictionary['practical date sheet']
    #