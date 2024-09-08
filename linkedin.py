from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
import random
import undetected_chromedriver as uc
import chromedriver_autoinstaller
import urllib.parse
from time import sleep
import os

# ---------------------------------------------------
keyword = "Python Backend Developer"
url = f"https://www.linkedin.com/jobs/search?keywords={urllib.parse.quote(keyword)}&location=Morocco&geoId=102787409&trk=public_jobs_jobs-search-bar_search-submit&position=1&pageNum=0"
anchors_xpath = "//a[contains(@href, '/jobs/view')]"
modal_dismiss_xpath = "//button[contains(@data-tracking-control-name, 'public_jobs_contextual-sign-in-modal_modal_dismiss')]"
title_xpath = "//h2[contains(@class, 'top-card-layout__title')]"
description_xpath = "//div[contains(@class, 'description__text')]"

# ---------------------------------------------------

def get_options():
    chrome_options = Options()
    width = random.randint(1000, 2000)
    height = random.randint(500, 1000)
    chrome_options.add_argument(f"window-size={width}, {height}")
    # chrome_options.add_experimental_option("useAutomationExtension", False)
    # chrome_options.add_argument("--disable-blink-features=AutomationControlled")
    # chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
    # chrome_options.add_argument('disable-infobars')
    # chrome_options.add_argument("--headless")
    # chrome_options.add_argument('--no-sandbox')
    # chrome_options.add_argument('--disable-dev-shm-usage')
    chrome_options.add_argument(
        "user-agent=Mozilla/5.0 (Windows NT 6.1; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/84.0.4147.125 Safari/537.36")
    return chrome_options


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
    clear_recent_temp_files(temp_dir, age_minutes=200)


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


if __name__ == '__main__':
    try:
        chrome_options = get_options()
        version_main = int(chromedriver_autoinstaller.get_chrome_version().split(".")[0])
        driver = uc.Chrome(options=chrome_options, version_main=version_main)
        driver.get(url)
        if check_exists_by_xpath(driver, modal_dismiss_xpath):
            click_forcefully(driver.find_element(By.XPATH, modal_dismiss_xpath), True, "//body")
        move_until_found(driver, anchors_xpath, 100)
        anchors = driver.find_elements(By.XPATH, anchors_xpath)
        for anchor in anchors:
            driver.execute_script("arguments[0].scrollIntoView();", anchor)
            click_forcefully(anchor, True, title_xpath)
            print(f"Link: {anchor.get_attribute("href")}")
            print(f"Title: {get_title(driver, title_xpath)}")
            print(f"Description: {get_description(driver, description_xpath)}")
            print("=====================================================================")
            sleep(random.uniform(2, 5))
        sleep(10)
        kill_chrome()
        driver.quit()
    except Exception as e:
        kill_chrome()
        raise e