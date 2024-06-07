from time import time
import json
import os

from .logger import *
from .pages import *
from .startup import Firefox
from .startup import FirefoxOptions



def scrape(UID, PASSWORD, download_folder='', save_to_file=True, filename='data',
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

    opts = FirefoxOptions()
    opts.add_argument("--headless")
    dr = Firefox(options=opts)
    dr.get('https://students.cuchd.in/?')
    dr.implicitly_wait(20)

    dictionary = {}

    dictionary['UID'] = UID
    dictionary['PASSWORD'] = PASSWORD

    info("Start scraping.")
    start = time()
    login(dr, UID, PASSWORD)

    if getall or homepage:
        get_homepage(dr, dictionary, download_path=download_folder, get_IDcard=download_IDcard)
    if getall or profile:
        get_profile(dr, dictionary, get_profile_pic)
    if getall or timetable:
        get_timetable(dr, dictionary)
    if getall or reg_marks:
        get_regular_marks(dr, dictionary)
    if getall or reg_results:
        get_regular_results(dr, dictionary)
    if getall or datesheet:
        get_datesheet(dr, dictionary)
    if getall or prac_datesheet:
        get_prac_datesheet(dr, dictionary)
    if getall or attendanc:
        get_attendance(dr, dictionary)
    if getall or hostel:
        get_hostel(dr, dictionary)

    dr.quit()
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
