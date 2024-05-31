from selenium.webdriver.common.by import By
from selenium.common.exceptions import *
from selenium.webdriver import Firefox
from PyPDF2 import PdfReader
from base64 import b64decode
from shutil import move
from io import BytesIO
from PIL import Image
from json import dump
import logging
import os


class Scraper:

    def __init__(self, driver, UID: str, password: str) -> None:
        logging.basicConfig(level=logging.INFO, filename='scraper.log', filemode='w',format="%(asctime)s -> %(levelname)s: %(message)s")

        logging.info("Making the scraper object.")
        
        self.dictionary = {}
        self.UID = UID
        self.password = password
        self.tries = 5000
        self.log = []

        # start the driver
        self.driver = driver()
        self.driver.get('https://students.cuchd.in/?')
        self.driver.implicitly_wait(10)
        logging.info("Website recived.")

        logging.info(f"Scraper object constructed successfully, with driver: {driver}, UID: {UID}, password: {password}, implicitly_wait: {10}, tries: {5000}")

        

    def __wait_for_loader(self):
        try:
            while True:
                self.driver.find_element(By.ID, 'loader-wrapper').click()
        except:
            return



    def __login(self) -> None:
        logging.info("Logging in...")

        logging.info("Locating, filling and posting UID form...")
        try:
            UID_input = self.driver.find_element(By.ID, 'txtUserId')
            UID_input.click()
            UID_input.send_keys(self.UID)
            next_btn = self.driver.find_element(By.ID, 'btnNext')
            next_btn.click()
            logging.info("Done.")
        except:
            logging.exception("Couldn't post UID form.")
        
        
        while True:
            try:
                logging.info("Locating, filling and posting password and captcha...")
                try:
                    pass_input = self.driver.find_element(By.ID, 'txtLoginPassword')
                    pass_input.click()
                    pass_input.send_keys(self.password)
                    logging.info("Password done.")
                except:
                    logging.exception("Couldn't fill password ")

                logging.info("Gettign captcha input from user")
                cap_input = self.driver.find_element(By.ID, 'txtcaptcha')
                cap_input.click()
                cap_input.clear()
                cap_input.send_keys(input('Enter the captcha: '))
            except:
                logging.exception("Couldn't fill captcha.")

            try:
                login = self.driver.find_element(By.ID, 'btnLogin')
                login.click()

                self.driver.implicitly_wait(3)
                try:
                    message = self.driver.find_element(By.CSS_SELECTOR, 'div[class="sweet-alert showSweetAlert visible"]')
                    message.find_element(By.CSS_SELECTOR, "button[class='confirm']").click()
                    logging.info("Wrong captcha. Redo...")
                except:
                    logging.info(f"Loged in successfully as {self.UID}")
                    break
            except:
                logging.exception("Couldn't log in.")
                


    def __get_homepage(self, download_path: str) -> None:

        logging.info("Moving to the home page.")
        for i in range(self.tries):
            try:
                # move to the home page
                home = self.driver.find_element(By.ID, 'aHome')
                self.driver.execute_script("arguments[0].click();", home)
                #

                # get mentor details
                logging.info("Getting mentor details.")
                for j in range(self.tries):
                    try:
                        list_items = self.driver.find_element(By.ID, 'divStudentMentorDetails')
                        list_items = list_items.find_elements(By.TAG_NAME, "li")
                        name = ''.join(list_items[0].text.split(' ')[2:])
                        email = ''.join(list_items[1].text.split(' ')[2:])
                        self.dictionary['mentor'] = {'name': name, 'email': email}
                        logging.info("Mentor details recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Mentor details couldn't be recived.")
                            self.dictionary['mentor'] = None
                        else:
                            pass                    
                # 

                # get important messages
                logging.info("Getting messages.")
                for j in range(self.tries):
                    try:
                        messages = self.driver.find_element(By.ID, 'divStudentMyMessages').find_element(By.TAG_NAME, 'ul').find_elements(By.TAG_NAME, 'li')
                        self.dictionary['messages'] = list({mess.text for mess in messages})
                        logging.info("Messages recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Messages couldn't be recived.")
                            self.dictionary['messages'] = None
                        else:
                            pass
                # 

                # download and move ID card to working directory
                logging.info("Getting ID card.")
                for j in range(self.tries):
                    try:
                        self.driver.find_element(By.ID, 'ContentPlaceHolder1_lbtnDownloadIdCard').click()
                        logging.info("Downloading ID card.")
                        for k in range(self.tries):
                            try:
                                for filename in os.listdir(download_path):
                                    if filename.startswith('Virtual_ID_Card_'):
                                        source_path = os.path.join(download_path, filename)
                                        destination_path = os.path.join(os.getcwd(), 'ID.pdf')
                                        for l in range(self.tries * 2):
                                            try:
                                                with open(source_path, 'rb') as pdf_file:
                                                    PdfReader(pdf_file) # If file is empty it raises an error
                                                    logging.info("ID card downloaded.")
                                                    try:
                                                        os.remove('ID.pdf')
                                                        logging.info("Previous ID card removed.")
                                                    except:
                                                        pass
                                                    move(source_path, destination_path)
                                                    logging.info("ID card recived successfully.")
                                                break
                                            except:
                                                if l == self.tries * 2 - 1:
                                                    logging.exception("ID card didn't download properly.")
                                                else:
                                                    pass
                                break
                            except:
                                if k == self.tries - 1:
                                    try:
                                        os.listdir(download_path)
                                        logging.exception(f"Directory ({download_path}) doesn't seem to be your download directory.")
                                    except:
                                        logging.exception(f"The directory {download_path} doesn't exist in your system.")
                                else:
                                    pass
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("ID card couldn't be downloaded.")
                        else:
                            pass
                #

                break
            except:
                if i == self.tries - 1:
                    logging.exception("Couldn't navigate to home page.")
                else:
                    pass
        # 


        
    def __get_profile(self) -> None:

        logging.info("Moving to profile page.")
        for i in range(self.tries):
            try:
                # Move to the profile page
                profile = self.driver.find_element(By.CSS_SELECTOR, 'div[class="user-dropdown"]').find_element(By.CSS_SELECTOR, 'a[href="frmStudentProfile.aspx"]')
                self.driver.execute_script("arguments[0].click();", profile)
                #

                # get profile picture
                logging.info("Getting profile picture.")
                for j in range(self.tries):
                    try:
                        lines = self.driver.find_elements(By.CLASS_NAME, 'row')
                        profile_pic = lines[0].find_element(By.TAG_NAME, 'img')
                        src_attribute = profile_pic.get_attribute('src')
                        base64_data = src_attribute.split(',')[1]
                        decoded_data = b64decode(base64_data)
                        image = Image.open(BytesIO(decoded_data))
                        try:
                            os.remove('profile_pic.png')
                            logging.info("Previous picture removed.")
                        except:
                            pass
                        image.save('profile_pic.png')
                        logging.info("Picture saved successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            try:
                                lines = self.driver.find_elements(By.CLASS_NAME, 'row')
                                logging.exception("Profile picture couldn't be downloaded.")
                            except:
                                logging.exception("No profile information found.")
                                self.dictionary['profile'] = None
                                return
                        else:
                            pass
                # 

                # get profile information
                logging.info("Getting profile information.")
                for j in range(self.tries):
                    try:
                        lines = self.driver.find_elements(By.CLASS_NAME, 'row')
                        self.dictionary['profile'] = {
                            lines[i + 1].find_elements(By.TAG_NAME, "div")[0].text:
                            lines[i + 1].find_elements(By.TAG_NAME, 'div')[1].text
                            for i in range(15)
                        }
                        logging.info("Profile information recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Profile informatiln couldn't be recived.")
                            pass
                        else:
                            pass
                # 

                # get qualifications
                logging.info("Getting qualifications.")
                for j in range(self.tries):
                    try:
                        table = self.driver.find_element(By.ID, 'ContentPlaceHolder1_gvStudentQualification')
                        rows = table.find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['profile']['qualifications'] = {
                            rows[0].find_elements(By.TAG_NAME, 'th')[j].text.lower():
                            [rows[i + 1].find_elements(By.TAG_NAME, 'td')[j].text for i in range(len(rows) - 1)]
                            for j in range(7)
                        }
                        logging.info("Qualifications recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Qualifications couldn't be recived.")
                            self.dictionary['profile']['qualifications'] = None
                        else:
                            pass  
                # 

                # get contacts
                logging.info("Getting contacts.")
                for j in range(self.tries):
                    try:
                        table = self.driver.find_element(By.ID, 'ContentPlaceHolder1_gvStudentContacts')
                        rows = table.find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['profile']['contacts'] = {
                            rows[0].find_elements(By.TAG_NAME, 'th')[j].text.lower():
                            [rows[i + 1].find_elements(By.TAG_NAME, 'td')[j].text for i in range(len(rows) - 1)]
                            for j in range(5)
                        }
                        logging.info("Contacts recived successfully")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Contacts couldn't be recived.")
                            self.dictionary['profile']['contacts'] = None
                        else:
                            pass
                # 

                break
            except:
                if i == self.tries - 1:
                    logging.exception("Couldn't navigate to the profile page.")
                    self.dictionary['profile'] = None
                else:
                    pass
        #



    def __get_timetable(self) -> None:

        logging.info("Moving to timetable page.")
        for i in range(self.tries):
            try:
                # Move to the timetable page
                timetable = self.driver.find_element(By.CSS_SELECTOR, 'a[href="frmMyTimeTable.aspx"]')
                self.driver.execute_script("arguments[0].click();", timetable)
                self.dictionary['timetable'] = {}
                #

                # get the hashmap
                logging.info("Getting the subjects hashmap.")
                for j in range(self.tries):
                    try:
                        rows = self.driver.find_element(By.ID, 'ContentPlaceHolder1_grdCourseDetail').find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['timetable']['hashmap'] = {
                            rows[i + 1].find_elements(By.TAG_NAME, 'td')[0].text:
                            rows[i + 1].find_elements(By.TAG_NAME, 'td')[1].text
                            for i in range(len(rows) - 1)
                        }
                        logging.info("Hashmap recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            self.dictionary['timetable']['hashmap'] = None
                            logging.exception("Subjects hashmap couldn't be recived.")
                        else:
                            pass
                #

                # get the Schedule
                logging.info("Getting the schedule.")
                for j in range(self.tries):
                    try:
                        rows = self.driver.find_element(By.ID, 'ContentPlaceHolder1_grdMain').find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['timetable']['Schedule'] = {
                            rows[0].find_elements(By.TAG_NAME, 'th')[i].text:
                            [rows[j + 1].find_elements(By.TAG_NAME, 'td')[i].text 
                            for j in range(len(rows) - 1)]
                            for i in range(8)
                        }
                        logging.info("Schedule recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            self.dictionary['timetable']['Schedule'] = None
                            logging.info("Schedule couldn't be recived.")
                        else:
                            pass
                #

                break
            except:
                if i == self.tries - 1:
                    logging.info("Couldn't navigate to the timetable page.")
                    self.dictionary['timetable'] = None
                else:
                    pass
        #



    def __get_attendance(self) -> None:

        logging.info("Moving to the attendance page.")
        for i in range(self.tries):
            try:
                # Move to the profile page
                attendance = self.driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudentCourseWiseAttendanceSummary.aspx?type=etgkYfqBdH1fSfc255iYGw=="]')
                self.driver.execute_script("arguments[0].click();", attendance)
                self.dictionary['attendance'] = {}
                #

                # get the attendance
                logging.info("Getting attendance.")
                main = False
                for j in range(self.tries):
                    try:
                        head = self.driver.find_element(By.ID, 'SortTable').find_elements(By.TAG_NAME, 'th')
                        rows = self.driver.find_element(By.ID, 'SortTable').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['attendance'] = {
                            head[i].text:
                            [rows[j].find_elements(By.TAG_NAME, 'td')[i].text 
                            for j in range(len(rows))]
                            for i in range(10)
                        }
                        if not main:
                            logging.info("Main attendance table recived successfully.")
                            logging.info("Getting full reports.")
                        main = True
                        
                        self.dictionary['attendance'][f'{head[-1].text}'] = []
                        for row in rows:
                            btn_not_found = False
                            for k in range(self.tries):
                                try:
                                    row.find_elements(By.TAG_NAME, 'td')[-1].click()
                                    self.__wait_for_loader()
                                    break
                                except:
                                    if k == self.tries - 1:
                                        logging.exception(f"Couldn't find full report button for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}")
                                        btn_not_found = True
                                    else:
                                        pass
                            if btn_not_found:
                                continue

                            for k in range(self.tries):
                                try:
                                    self.driver.implicitly_wait(0)
                                    self.driver.find_element(By.CSS_SELECTOR, "button[class='confirm']").click()
                                    self.dictionary['attendance'][f'{head[-1].text}'].append(None)
                                    logging.info(f"Couldn't find full report for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}")
                                    break
                                except:
                                    pass
                                try:
                                    top = self.driver.find_element(By.ID, 'fullreport').find_elements(By.TAG_NAME, 'th')
                                    lines = self.driver.find_element(By.ID, 'fullreport').find_element(By.TAG_NAME, 'tbody').find_elements(By.TAG_NAME, 'tr')
                                    self.dictionary['attendance'][f'{head[-1].text}'].append({
                                        top[i].text:
                                        [lines[j].find_elements(By.TAG_NAME, 'td')[i].text 
                                        for j in range(len(lines))]
                                        for i in range(8)
                                    })
                                    
                                    self.driver.find_element(By.ID, 'popupid').find_element(By.CLASS_NAME, 'closebtn').click()
                                    logging.info(f"Recived full report for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}")
                                    break
                                except Exception as e:
                                    if k == self.tries - 1:
                                        logging.critical(f"Panic: Couldn't exit current fullreport for subject: {row.find_elements(By.TAG_NAME, 'td')[0].text}\n{e}")
                                        exit(1)
                                    else:
                                        pass
                        logging.info("Attendance fetched successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            self.dictionary['attendance'] = None
                            logging.exception("Attendance couldn't be recived.")
                        else:
                            pass
                #

                break
            except:
                if i == self.tries - 1:
                    self.dictionary['attendance'] = None
                    logging.exception("Couldn't navigate to the attendance page.")
                else:
                    pass
        #



    def __get_hostel(self) -> None:

        logging.info("Moving to hostel page.")
        for i in range(self.tries):
            try:
                # Move to the hostel page
                hostel = self.driver.find_element(By.CSS_SELECTOR, 'a[href="frmStudenHostelDetails.aspx"]')
                self.driver.execute_script("arguments[0].click();", hostel)
                #

                # get the table
                logging.info("Getting hostel details")
                for j in range(self.tries):
                    try:
                        rows = self.driver.find_element(By.CSS_SELECTOR, 'table[class="table table-bordered table-hover text-center tblHostelDetails"]').find_elements(By.TAG_NAME, 'tr')
                        self.dictionary['hostel'] = {
                            rows[i].find_element(By.TAG_NAME, 'th').text:
                            rows[i].find_element(By.TAG_NAME, 'td').text
                            for i in range(len(rows))
                        }
                        logging.info("Hostel details recived successfully.")
                        break
                    except:
                        if j == self.tries - 1:
                            logging.exception("Couldn't recive hostel details.")
                            self.dictionary['hostel'] = None
                        else:
                            pass
                #
        
                break
            except:
                if i == self.tries - 1:
                    logging.info("Couldn't navigate to the hostel page.")
                    self.dictionary['hostel'] = None
                else:
                    pass
        #




    def scrape(self, your_download_folder: str) -> None:
        logging.info("Start scraping.")

        self.__login()
        # self.__get_profile()
        # self.__get_timetable()
        # self.__get_attendance()
        self.__get_hostel()
        # self.__get_homepage(download_path=your_download_folder)

        self.driver.quit()

        try:
            os.remove('data.json')
        except:
            pass

        with open('data.json', 'w') as outfile:
            dump(self.dictionary, outfile)

        logging.info('Scrapping Done.')



if __name__ == '__main__':

    scraper = Scraper(driver=Firefox, UID='23BIS70139', password='01.Jan.2005')
    scraper.scrape('/home/ayman/Downloads/')
  