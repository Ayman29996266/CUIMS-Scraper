from ..logger import *
from ..startup import StaleElementReferenceException
from ..startup import NoSuchElementException
from ..startup import By
from ..startup import wait_for_loader



def get_hostel(driver, dictionary) -> None:

    info("Moving to hostel page.")
    try:
        # Move to the hostel page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudenHostelDetails.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        #

        # get the table
        info("Getting hostel details")
        try:
            itr = 0
            while True:
                try:
                    table = driver.find_element(By.TAG_NAME, 'table')
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    dictionary['hostel'] = {
                        rows[i].find_element(By.TAG_NAME, 'th').text:
                        rows[i].find_element(By.TAG_NAME, 'td').text
                        for i in range(len(rows))
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

            info("Hostel details recived successfully.")
        except:
            exception("Couldn't recive hostel details.")
            dictionary['hostel'] = None
        #
    except:
        exception("Couldn't navigate to the hostel page.")
        dictionary['hostel'] = None
    #
