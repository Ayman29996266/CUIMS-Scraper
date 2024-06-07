# Chandigarh University Student Information Scraper (CUIMS)


This Python-based web scraper automates the process of retrieving student information from Chandigarh University's CUIMS portal.

This tool is ideal for students working on personal projects or designing dashboards that is centered around the students information.




**Features:**


* **Automated Captcha Handling:** Streamlines data retrieval by auto solving CAPTCHA.

* **Robust Exception Handling:** Ensures the scraper gracefully handles potential errors, improving reliability.

* **JSON Output:** Generates a well-structured JSON file containing the extracted student information, facilitating convenient data manipulation and analysis.

* **Logged Progress:** Stores its progress, reports and errors encountered in a log file for easier trouble shooting.



## Installation


1. **Prerequisites:** Ensure you have Python 3.x and pip installed on your system. You can verify this by running `python --version` and `pip --version` in your terminal. Then, recommended, set a python virtual environment in your working directory by running `python -m venv "name"` and then activate it in your current terminal session by running this in the same directory `source "name"/bin/activate`

2. **Install Dependencies:** Use `pip` to install the required libraries:
  ```bash
  pip install selenium selenium pillow pypdf2 easyocr
  ```

3. **Clone The Repository:**Run the following command in the same working directory to clone the repository:
  ```bash
  git clone [invalid URL removed]
  ```

## Usage


1. **Make Python file:** Create a new python file and import the "scrape" function from the repository folder:
  ```python
  from CUIMS-scraper.cuims_scraper import scrape
  ```

2. **Customize the function:** Enter your student UID and password, Then tune the function parameters for the desired information you wish to retrieve. See the example_usage.py file for examples.


### Function parameters:


*- UID:*                 Student UID.
*- PASSWORD:*            Student password.

*- save_to_file:*        Whither the function will save the collected data in a json file or not. Either way, the function will return the scraped data as a python dictionary.
*- filename:*            The name of the json file to save data in.
*- overwrite:*           Overwrite the previous json file (if found) or not. If not, new ones come enumerated.

*- homepage:*            Scrape info in homepage (mentor) (messages).
*- download_IDcard:*     Download ID card from homepage or not.
*- download_folder:*     Your browser download folder.

*- profile:*             Scrape student profile.
*- get_profile_pic:*     Get the student profile picture from profile.

*- attendance:*          Scrape students attendance.
*- timetable:*           Scrape students time table.
*- datesheet:*           Scrape students date sheet.
*- prac_datesheet:*      Scrape students practical date sheet.
*- reg_marks:*           Scrape students regular marks.
*- reg_results:*         Scrape students regular results.
*- hostel:*              Scrape students hostel info.

(NOTE: if all scrape options are set to False or left unfilled, the function will set them all to True automatically)

3. **Run the file:** Use your favorite text editor to run the file. Or, go back to your terminal and run the file by typing `python file.py` and see your information being collected!
4. **Output:** Depending on how you tuned your function, you can see the students profile picture in a png format, the student ID card in a pdf format and all text information you asked for in a neatly organized json format file.


## More

* It's worth noting that, like all web scrapers, a small change in the CUIMS website layout will can severely impact the package functionality.
* The package has been tested on the latest update for the website and it works like a charm (07/Jun/2024).
* This python package will probably not be maintained regularly, as owner and founder will graduate and loose his access to the site.
* If the website got updated, or you have brilliant ideas to add, feel free to become part of this project and update it accordingly.


## Disclaimer

*This scraper is intended for educational purposes and personal projects. Please use it responsibly and adhere to Chandigarh University's terms and conditions regarding data usage and scraping. Be mindful of scraping large amounts of data that could overload their servers.*
