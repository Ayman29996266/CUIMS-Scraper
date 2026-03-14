from cuims_scraper import scrape


if __name__ == "__main__":

    scrape(
        UID="23BIS70139",
        PASSWORD="01Jan2005@",
        save_to_file=True,
        overwrite=True,

        download_IDcard=True,
        get_profile_pic=True,

        profile=False,
        timetable=False,
        reg_marks=False,
        reg_results=False,
        datesheet=False,
        prac_datesheet=False,
        attendanc=False,
        hostel=True,
        homepage=True,
    )
