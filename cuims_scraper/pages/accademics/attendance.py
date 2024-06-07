from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_attendance(driver, dictionary) -> dict:

    info("Moving to the attendance page.")
    try:
        # Move to the attendance page
        page = driver.find_element(By.ID, 'menu-content').find_element(By.TAG_NAME, 'ul').find_element(By.TAG_NAME, 'a')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        dictionary['attendance'] = {};
        #

        # get the attendance
        info("Getting attendance.")
        try:
            itr = 0
            while True:
                try:
                    head = driver.find_element(By.ID, 'SortTable').find_elements(By.TAG_NAME, 'th')
                    rows = driver.find_element(By.ID, 'SortTable').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                    dictionary['attendance'] = {
                        head[i].text:
                        [rows[j].find_elements(By.TAG_NAME, 'td')[i].text 
                        for j in range(len(rows))]
                        for i in range(10)
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

            info("Main attendance table recived successfully.")
            info("Getting full reports.")
            
            dictionary['attendance'][f'{head[-1].text}'] = []
            for row in rows:
                try:
                    wait_for_loader(driver)
                    row.find_elements(By.TAG_NAME, 'td')[-1].click()
                    wait_for_loader(driver)
                except:
                    exception(f"Couldn't find full report button for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}")
                    continue

                for k in range(10):
                    try:
                        driver.find_element(By.CSS_SELECTOR, "button[class='confirm']").click()
                        dictionary['attendance'][f'{head[-1].text}'].append(None)
                        warning(f"Subject: {row.find_elements(By.TAG_NAME, 'td')[0].text} doesn't have a full report.")
                        break
                    except:
                        pass
                    try:
                        wait_for_loader(driver)
                        top = driver.find_element(By.ID, 'fullreport').find_elements(By.TAG_NAME, 'th')
                        lines = driver.find_element(By.ID, 'fullreport').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                        dictionary['attendance'][f'{head[-1].text}'].append({
                            top[i].text:
                            [lines[j].find_elements(By.TAG_NAME, 'td')[i].text 
                            for j in range(len(lines))]
                            for i in range(8)
                        })
                        
                        driver.find_element(By.ID, 'popupid').find_element(By.CLASS_NAME, 'closebtn').click()
                        info(f"Recived full report for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}")
                        break
                    except Exception as e:
                        if k == 9:
                            critical(f"Panic: Couldn't exit current fullreport for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}\n{e}")
                            exit(1)
                        else:
                            pass

            info("Attendance fetched successfully.")
            return dictionary['attendance']
        except:
            dictionary['attendance'] = None
            exception("Attendance couldn't be recived.")
            return dictionary['attendance']
        #
    except:
        dictionary['attendance'] = None
        exception("Couldn't navigate to the attendance page.")
        return dictionary['attendance']
    #
