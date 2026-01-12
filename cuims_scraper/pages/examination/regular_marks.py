from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_regular_marks(driver, dictionary) -> dict:

    log_info("Moving to regular marks page.")
    try:
        # Move to the regular marks page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudentMarksView.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        dictionary['regular marks'] = {}
        #

        # get the regular marks
        log_info("Getting the regular marks.")
        try:
            itr = 0
            while True:
                try:
                    wait_for_loader(driver)
                    accordion = driver.find_element(By.ID, 'accordion')
                    h3s = accordion.find_elements(By.TAG_NAME, 'h3')
                    divs = accordion.find_elements(By.TAG_NAME, 'div')
                    for i, (h3, div) in enumerate(zip(h3s, divs)):
                        if i:
                            h3.click()
                        heads = div.find_elements(By.TAG_NAME, 'th')
                        body_rows = div.find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                        dictionary['regular marks'][f"{h3.text.split(' ')[-1][1:-1]}"] = {
                            heads[i].text:
                            [body_rows[j].find_elements(By.TAG_NAME, 'td')[i].text for j in range(len(body_rows))]
                            for i in range(len(heads))
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

            log_info("Regular marks recived successfully.")
            return dictionary['regular marks']
        except:
            dictionary['regular marks'] = None
            log_exception("Regular marks couldn't be recived.")
            return dictionary['regular marks']
        #
    except:
        log_exception("Couldn't navigate to the regular marks page.")
        dictionary['regular marks'] = None
        return dictionary['regular marks']
    #