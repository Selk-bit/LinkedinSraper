import shutil
import time
import psutil
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import random
from time import sleep
import os

from urllib3 import request

from constants import main_url, anchors_xpath, modal_dismiss_xpath, card_port_xpath, job_title_xpath, \
    job_company_name_xpath, job_description_xpath, job_description_xpath, job_location_xpath, job_age_xpath
from utils import ChromeDriver, LinkedScrapper
import requests


def get_link():
    pass


def get_title(dr, xpath):
    try:
        return dr.find_element(By.XPATH, xpath).text.strip()
    except AttributeError as e:
        print(e)
        return None


def get_description(dr, xpath):
    try:
        return dr.find_element(By.XPATH, xpath).text
    except AttributeError as e:
        return None


def get_city():
    pass


def get_work_mode():
    pass


def get_company_name():
    pass


def get_post_date():
    pass


def check_exists_by_xpath(driver, xpath):
    try:
        driver.find_element(By.XPATH, xpath)
    except NoSuchElementException:
        return False
    return True


def move_until_found(driver, xpath, count):
    counter = 0
    while True:
        if check_exists_by_xpath(driver, xpath):
            break
        # driver.get(url)
        counter += 1
        if counter == count:
            raise Exception(f"Element not found: {xpath} after 100 attempts")
        sleep(random.uniform(0.1, 0.9))


def clear_recent_temp_files(temp_dir, age_minutes=2):
    current_time = time.time()
    age_seconds = age_minutes * 60

    for root, dirs, files in os.walk(temp_dir):
        for name in files + dirs:
            full_path = os.path.join(root, name)
            try:
                # Get the creation time of the file/directory
                creation_time = os.path.getctime(full_path)

                # Check if the file/directory was created within the last 'age_minutes' minutes
                if (current_time - creation_time) < age_seconds:
                    if os.path.isfile(full_path) or os.path.islink(full_path):
                        os.remove(full_path)
                    elif os.path.isdir(full_path):
                        shutil.rmtree(full_path)
                    print(f"Deleted: {full_path}")
            except Exception as e:
                print(f"Failed to delete {full_path}. Reason: {e}")


def kill_chrome_processes():
    # Iterate over all running processes
    for proc in psutil.process_iter(['pid', 'name']):
        try:
            # Check if process name contains "chrome"
            if 'chrome' in proc.info['name'].lower():
                # Terminate the process
                proc.kill()
                print(f"Killed process {proc.info['name']} with PID {proc.info['pid']}")
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass


def kill_chrome(driver):
    driver.close()
    driver.quit()
    kill_chrome_processes()
    clear_recent_temp_files("~/.config/google-chrome/smarteez/Application Cache/Cache/", age_minutes=200)


def click_forcefully(dr, limit, xpath):
    counter = 0
    while True:
        try:
            driver.execute_script("arguments[0].click();", dr)
            # dr.click()
            if check_exists_by_xpath(dr, xpath):
                return True
        except Exception as e:
            print("Couldn't Click")
            pass
        counter += 1
        if limit and counter == 50:
            return False


def get_job_urls(driver):
    driver.get(main_url)
    if check_exists_by_xpath(driver, modal_dismiss_xpath):
        click_forcefully(driver.find_element(By.XPATH, modal_dismiss_xpath), True, "//body")
    move_until_found(driver, anchors_xpath, 100)
    anchors = driver.find_elements(By.XPATH, anchors_xpath)
    # for anchor in anchors:
    #     driver.execute_script("arguments[0].scrollIntoView();", anchor)
    #     # click_forcefully(anchor, True, card_port_xpath)
    #     job_urls.append(anchor.get_attribute('href'))
    return [anchor.get_attribute('href') for anchor in anchors]

    # return job_urls


if __name__ == '__main__':
    try:
        print(f"start")
        driver = ChromeDriver().get_driver()
        print(f"start 2")
        job_urls = get_job_urls(driver)
        print(f"start 3")

        if 'Sign Up' in driver.page_source:
            print('Sign Up')
            exit(0)

        linked_scrapper = LinkedScrapper()
        print(f"{linked_scrapper=}")
        for url in job_urls:

            driver.get(url)
            if check_exists_by_xpath(driver, modal_dismiss_xpath):
                click_forcefully(driver.find_element(By.XPATH, modal_dismiss_xpath), True, "//body")

            job_title = linked_scrapper.get_one_element(driver, job_title_xpath)
            job_description = linked_scrapper.get_one_element(driver, job_description_xpath, True)
            company_name = linked_scrapper.get_one_element(driver, job_company_name_xpath)
            job_location = linked_scrapper.get_one_element(driver, job_location_xpath)
            job_age = linked_scrapper.get_one_element(driver, job_age_xpath)

            data = {'job_title': job_title, 'job_description': job_description, 'company_name': company_name,
                    'job_location': job_location, 'job_age': job_age}

            print(f"{data=}")
            sleep(3)

        kill_chrome(driver)
        driver.quit()
    except Exception as e:
        # kill_chrome(driver=driver)

        print(e)
        sleep(9999)
