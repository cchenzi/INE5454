"""Process to acquire the authorization cookie for a service in UFSC

The authentication is made using selenium webdriver because
we have some hard times trying to authenticate using requests.
"""
from typing import Dict
from urllib.parse import quote as url_encode

from selenium import webdriver

from config import settings


def fetch_cookie(service: str) -> Dict[str, str]:
    """Execute a Selenium webdriver to get the authentication cookie

    User and password are set in config file

    Args:
        service (str): url of the desired service

    Returns:
        Dict[str, str]: Auth headers to use in requests to system
    """
    options = webdriver.ChromeOptions()
    options.headless = True
    driver = webdriver.Chrome(options=options)
    driver.get(settings.auth_url.format(url_encode(service)))

    username_input = driver.find_element(by='id', value="username")
    username_input.send_keys(settings.auth_username)

    password_input = driver.find_element(by='id', value="password")
    password_input.send_keys(settings.auth_password)

    submit_button = driver.find_element(by='name', value="submit")
    submit_button.click()

    return {
        cookie['name']: cookie['value']
        for cookie in driver.get_cookies()
    }
