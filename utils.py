import shutil
import time
from typing import Optional

import psutil
import selenium
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

from constants import scrapping_source


class ChromeDriver:

    def __init__(self):
        self.chrome_options = self.get_options()
        self.version_main = int(chromedriver_autoinstaller.get_chrome_version().split(".")[0])
        self.driver = uc.Chrome(options=self.chrome_options, version_main=self.version_main)

    @staticmethod
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

    def get_driver(self):
        return self.driver


class LinkedInJobScrapper:
    @staticmethod
    def get_one_element(driver: uc.Chrome, xpath: str, using_js=False) -> Optional[str]:
        driver_elements = driver.find_element(By.XPATH, xpath)
        if driver_elements:
            if using_js:
                text = driver.execute_script("""
                    const parentElement = arguments[0];
                    const childElements = parentElement.querySelectorAll('*');
                    let combinedText = '';

                    childElements.forEach(element => {
                        // Get the content of the ::marker pseudo-element if present
                        let marker = window.getComputedStyle(element, '::marker').getPropertyValue('content');

                        // If marker is present, clean it by removing unwanted default values or characters
                        if (marker && marker !== 'normal' && marker !== 'none' && marker.trim() !== '') {
                            marker = marker.replace(/["'.,·•●○■◆★✔︎•]/g, '').trim();
                        } else {
                            marker = ''; // Ignore if it matches unwanted defaults or is empty
                        }

                        // Get the text content of the element
                        const textContent = element.textContent.trim();

                        // Combine cleaned marker content and text content
                        const elementText = (marker ? marker + ' ' : '') + textContent;

                        // Append the text of each element followed by a newline
                        if (elementText) {
                            combinedText += elementText + '\\n';
                        }
                    });

                    return combinedText.trim();  // Trim to remove any trailing newline
                """, driver_elements)
                return text.split("Show less", 1)[-1].strip()
            else:
                return driver_elements.text.strip()
        return None

    @staticmethod
    def get_multiple_elements(driver: uc.Chrome, xpath: str) -> Optional[str]:
        driver_elements = driver.find_elements(By.XPATH, xpath)
        if driver_elements:
            for driver_element in driver_elements:
                return driver_element.text.strip()
        return None


class LinkedScrapper(LinkedInJobScrapper):
    def __init__(self):
        self.source = scrapping_source
