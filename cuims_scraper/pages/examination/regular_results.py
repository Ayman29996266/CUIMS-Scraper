from ...logger import *
from ...startup import StaleElementReferenceException
from ...startup import NoSuchElementException
from ...startup import By
from ...startup import wait_for_loader



def get_regular_results(driver, dictionary) -> dict:

    info("Moving to regular results page.")
    try:
        # Move to the regular results page
        page = driver.find_element(By.CSS_SELECTOR, 'a[href="result.aspx"]')
        driver.execute_script("arguments[0].click();", page)
        wait_for_loader(driver)
        dictionary['regular results'] = {}
        #

        # get the regular results
        info("Getting the regular results.")

        # itr = 0
        # while True:
        #     try:
        #         options = driver.find_element(By.TAG_NAME, 'select')
        #         options.click()
        #         options.find_elements(By.TAG_NAME, 'option')[0].click()
        #         wait_for_loader(driver)
        #         btn = driver.find_element(By.CSS_SELECTOR, 'input[type="submit"]')
        #         driver.execute_script("arguments[0].click();", btn)
        #         wait_for_loader(driver)
        #         break
        #     except StaleElementReferenceException:
        #         pass
        #     except NoSuchElementException as e:
        #         itr += 1
        #         if itr 49:
        #             raise e
        #         else:
        #             pass
        #     except Exception as e:
        #         exception("Couldn't get the per session regular results.")
        #         raise e

        try:
            itr = 0
            while True:
                try:
                    dictionary['regular results']['CGPA'] = driver.find_elements(By.CLASS_NAME, "from-control")[7].text.split(' ')[-1]
                    info("CGPA recived successfully.")
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
                    dictionary['regular results']['CGPA'] = None
                    exception("Couldn't recive CGPA.")
                    break


            rows = len(driver.find_elements(By.CSS_SELECTOR, '#result > div > table > tbody > tr')) * 1
            for k in range(rows):
                itr = 0
                while True:
                    try:
                        sems = driver.find_elements(By.CSS_SELECTOR, '#result > div > table > tbody > tr')
                        sgpa = sems[k].find_elements(By.TAG_NAME, 'div')[0].text.split(' ')[-1]

                        subs = sems[k].find_elements(By.TAG_NAME, 'tr')
                        heads = subs[0].find_elements(By.TAG_NAME, 'th')
                        subs = subs[1:]
                        dictionary['regular results'][f"semester_{k + 1}"] = {
                            heads[i].text:
                            [subs[j].find_elements(By.TAG_NAME, 'td')[i].text for j in range(len(subs))]
                            for i in range(len(heads))
                        }
                        break
                    except StaleElementReferenceException as e:
                        pass
                    except NoSuchElementException as e:
                        itr += 1
                        exception()
                        if itr == 50:
                            raise e
                        else: 
                            pass
                    except Exception as e:
                        raise e

                if sgpa == ':':
                    error("Couldn't recive SGPA.")
                    dictionary['regular results'][f"semester_{k + 1}"]["SGPA"] =  None
                else:
                    dictionary['regular results'][f"semester_{k + 1}"]["SGPA"] = sgpa

            info("regular Results recived successfully.")
            return dictionary['regular results']
        except:
            dictionary['regular results'] = None
            exception("regular Results couldn't be recived.")
            return dictionary['regular results']
        #
    except:
        exception("Couldn't navigate to the regular results page.")
        dictionary['regular results'] = None
        return dictionary['regular results']
    #