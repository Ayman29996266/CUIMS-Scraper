from time import time
import json
import os

from .logger import *
from .pages import *

from selenium.webdriver import Firefox
from selenium.webdriver import FirefoxOptions


def scrape(UID, PASSWORD, save_to_file=True, filename='data',
           overwrite=True, download_IDcard=True, get_profile_pic=True,
           profile=False, timetable=False, reg_marks=False, reg_results=False,
           datesheet=False, prac_datesheet=False, attendanc=False, hostel=False,
           homepage=False) -> dict:
    
    '''
    Arguments:
    
        - UID:                  Student UID.                                        (str)
        - PASSWORD:             Student password.                                   (str)

        - save_to_file:         Whither the function will save the collected
                                data in a json file or not. Either way, the
                                function will return the scraped data as a
                                python dictionary                                   (bool)
        - filename:             The name of the json file to save data in.          (str)
        - overwrite:            Overwrite the previous json file (if found).
                                or not. If not, new ones come enumerated.           (bool)

        - homepage:             Scrape info in homepage (mentor) (messages).        (bool)
        - download_IDcard:      Download ID card from homepage or not.              (bool)
        - download_folder:      Your browser download folder.                       (str)

        - profile:              Scrape student profile.                             (bool)
        - get_profile_pic:      Get the student profile picture from profile.       (bool)

        - attendance:           Scrape students attendance.                         (bool)
        - timetable:            Scrape students time table.                         (bool)
        - datesheet:            Scrape students date sheet.                         (bool)
        - prac_datesheet:       Scrape students practical date sheet.               (bool)
        - reg_marks:            Scrape students regular marks.                      (bool)
        - reg_results:          Scrape students regular results.                    (bool)
        - hostel:               Scrape students hostel info.                        (bool)

                                (NOTE: if all scrape options are set to False,
                                the function will set them all to True)
    '''
    
    
    getall = not (profile or timetable or reg_marks or reg_results or datesheet or prac_datesheet or attendanc or hostel or homepage)

    download_dir = os.path.abspath(os.getcwd())

    driver_options = FirefoxOptions()
    driver_options.add_argument("--headless")
    driver_options.set_preference("browser.download.folderList", 2)                     # allow custom download folder
    driver_options.set_preference("browser.download.dir", download_dir)                 # set custom download folder
    driver_options.set_preference("browser.download.useDownloadDir", True)              # use custom download folder
    driver_options.set_preference("browser.download.manager.showWhenStarting", False)   # no UI
    driver_options.set_preference("pdfjs.disabled", True)                               # force disable pdf viewer
    driver_options.set_preference(                                                      # auto-save MIME types
        "browser.helperApps.neverAsk.saveToDisk",
        "application/pdf,application/octet-stream"
    )

    driver = Firefox(options=driver_options)
    driver.get('https://students.cuchd.in/?')
    driver.implicitly_wait(20)

    dictionary = {}

    dictionary['UID'] = UID
    dictionary['PASSWORD'] = PASSWORD

    info("Start scraping.")
    start = time()
    login(driver, UID, PASSWORD)

    if getall or homepage:
        get_homepage(driver, dictionary, download_id_file=download_IDcard)
    if getall or profile:
        get_profile(driver, dictionary, get_profile_pic)
    if getall or timetable:
        get_timetable(driver, dictionary)
    if getall or reg_marks:
        get_regular_marks(driver, dictionary)
    if getall or reg_results:
        get_regular_results(driver, dictionary)
    if getall or datesheet:
        get_datesheet(driver, dictionary)
    if getall or prac_datesheet:
        get_prac_datesheet(driver, dictionary)
    if getall or attendanc:
        get_attendance(driver, dictionary)
    if getall or hostel:
        get_hostel(driver, dictionary)

    driver.quit()
    end = time()


    if save_to_file:
        name = dictionary['UID'] + '_' + filename
        if not overwrite:
            counter = 1
            while os.path.exists(f"{name}.json"):
                name = f"{name}_{counter}"
                counter += 1
        with open(f"{name}.json", "w") as f:
            json.dump(dictionary, f, indent=4)


    info(f'Scraping Done in {int(end - start)} s.')
    return dictionary
