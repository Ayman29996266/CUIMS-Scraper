from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_timetable(driver, dictionary) -> dict:

    info("Moving to timetable page.")
    try:
        # Move to the timetable page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="frmMyTimeTable.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)

        while True:
            try:
                assert driver.find_element(By.CSS_SELECTOR, '.container-fluid > div:nth-child(2)').text == 'My Time Table'
                break
            except AssertionError:
                pass
            except StaleElementReferenceException:
                pass
            except Exception as e:
                raise e

        dictionary['timetable'] = {}
        #

        # get the hashmap
        info("Getting the subjects hashmap.")
        try:
            itr = 0
            while True:
                try:
                    table = driver.find_element(By.CLASS_NAME, 'container-fluid').find_elements(By.TAG_NAME, 'table')[1]
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    rows[1].find_elements(By.TAG_NAME, 'td')[0].text
                    dictionary['timetable']['hashmap'] = {
                        rows[i + 1].find_elements(By.TAG_NAME, 'td')[0].text:
                        rows[i + 1].find_elements(By.TAG_NAME, 'td')[1].text
                        for i in range(len(rows) - 1)
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

            info("Hashmap recived successfully.")
        except:
            dictionary['timetable']['hashmap'] = None
            exception("Subjects hashmap couldn't be recived.")
        #

        # get the Schedule
        info("Getting the schedule.")
        try:
            itr = 0
            while True:
                try:
                    table = driver.find_element(By.CLASS_NAME, 'container-fluid').find_elements(By.TAG_NAME, 'table')[0]
                    rows = table.find_elements(By.TAG_NAME, 'tr')
                    dictionary['timetable']['Schedule'] = {
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

            info("Schedule recived successfully.")
            return dictionary['timetable']
        except:
            dictionary['timetable']['Schedule'] = None
            exception("Schedule couldn't be recived.")
            return dictionary['timetable']
        #

    except:
        exception("Couldn't navigate to the timetable page.")
        dictionary['timetable'] = None
        return dictionary['timetable']
    #
