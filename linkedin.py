# linkedin.py
import shutil
import time
from typing import List

import psutil
from selenium.common.exceptions import NoSuchElementException
from selenium.webdriver.common.by import By
import random
from time import sleep
import os
from constants import main_url, anchors_xpath, modal_dismiss_xpath, job_title_xpath, job_company_name_xpath, \
    job_description_xpath, job_location_xpath, job_age_xpath, url_index_spliter
from db_management.insert_data import session
from db_management.models import LinkedInCompany, LinkedInJob
from serializers import CompanySerializer, JobSerializer, ScrapingJobResultSerializer
from utils import ChromeDriver, LinkedScrapper


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


def get_job_urls(driver) -> List[str]:
    driver.get(main_url)
    if check_exists_by_xpath(driver, modal_dismiss_xpath):
        click_forcefully(driver.find_element(By.XPATH, modal_dismiss_xpath), True, "//body")
    move_until_found(driver, anchors_xpath, 100)
    anchors = driver.find_elements(By.XPATH, anchors_xpath)
    raw_urls = [anchor.get_attribute('href') for anchor in anchors]
    urls = []
    for url_str in raw_urls:
        if url_index_spliter in url_str:
            urls.append(url_str.split(url_index_spliter)[0])
            continue
        urls.append(url_str)
    return urls


if __name__ == '__main__':
    number_of_scrapped_jobs = 0
    driver = ChromeDriver().get_driver()
    try:
        job_urls = get_job_urls(driver)

        if 'Sign Up' in driver.page_source:
            scraping_job_results_serializer = ScrapingJobResultSerializer.model_construct(
                **{'number_of_jobs': 0, 'exited_with_error': True, 'error_message': "'Sign Up' in driver.page_source"})
            scraping_job_results_serializer.validate()
            scraping_job_results_serializer.save()
            exit(0)

        linked_scrapper = LinkedScrapper()
        for url in job_urls:

            job = session.query(LinkedInJob).filter_by(url=url).first()
            if job:
                continue
            driver.get(url)
            if check_exists_by_xpath(driver, modal_dismiss_xpath):
                click_forcefully(driver.find_element(By.XPATH, modal_dismiss_xpath), True, "//body")

            job_title = linked_scrapper.get_one_element(driver, job_title_xpath)
            job_description = linked_scrapper.get_one_element(driver, job_description_xpath, True)
            company_name = linked_scrapper.get_one_element(driver, job_company_name_xpath)
            job_location = linked_scrapper.get_one_element(driver, job_location_xpath)
            job_age = linked_scrapper.get_one_element(driver, job_age_xpath)

            company = None
            if all([company_name, isinstance(company_name, str)]):
                company_name = company_name.lower().strip()

                # Check if the company already exists
                company = session.query(LinkedInCompany).filter_by(raison_social=company_name).first()
                if not company:
                    company_serializer = CompanySerializer.model_construct(raison_social=company_name)
                    if company_serializer.validate():
                        company = company_serializer.save()
                    else:
                        scraping_job_results_serializer = ScrapingJobResultSerializer.model_construct(
                            **{'number_of_jobs': number_of_scrapped_jobs, 'exited_with_error': True,
                               'error_message': company_serializer.errors_text()})
                        scraping_job_results_serializer.validate()
                        scraping_job_results_serializer.save()
                        exit()

            data = {'title': job_title, 'description': job_description, 'location': job_location, 'age': job_age,
                    'url': url, 'company_id': company.id if company else None}

            # Insert the job into the LinkedInJob table
            job = session.query(LinkedInJob).filter_by(url=url).first()
            if not job:
                job_serializer = JobSerializer.model_construct(**data)
                if job_serializer.validate():
                    job = job_serializer.save()
                    number_of_scrapped_jobs += 1
                else:

                    scraping_job_results_serializer = ScrapingJobResultSerializer.model_construct(
                        **{'number_of_jobs': number_of_scrapped_jobs, 'exited_with_error': True,
                           'error_message': job_serializer.errors_text()})
                    scraping_job_results_serializer.validate()
                    scraping_job_results_serializer.save()

                    exit()
            sleep(3)

    except Exception as e:
        scraping_job_results_serializer = ScrapingJobResultSerializer.model_construct(
            **{'number_of_jobs': number_of_scrapped_jobs, 'exited_with_error': True,
               'error_message': str(e)})
        scraping_job_results_serializer.validate()
        scraping_job_results_serializer.save()
        raise e
    finally:
        session.close()
        kill_chrome(driver)
        driver.quit()
