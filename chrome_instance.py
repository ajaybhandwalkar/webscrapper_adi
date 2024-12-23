import undetected_chromedriver as uc
from selenium.common import TimeoutException
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from undetected_chromedriver import ChromeOptions
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from logger import init_logger

logger = init_logger()


def web_wait_for_element(driver, by, value, timeout=10):
    try:
        ele = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return ele
    except TimeoutException as te:
        logger.error(f"Element not found {by, value}")
        return False


def web_wait_for_elements(driver, by, value, timeout=10) -> list:
    try:
        ele = WebDriverWait(driver, timeout).until(EC.presence_of_all_elements_located((by, value)))
        return ele
    except TimeoutException as te:
        logger.error(f"Element not found {by, value}")
        return False



def get_undetected_chrome_driver():
    """
    Fetch undetected_chrome driver
    Returns undetected_chrome driver
    """
    try:
        chrome_options = ChromeOptions()
        chrome_options.add_argument("--disable-popup-blocking")  # Disable pop-up blocking
        chrome_options.add_argument("--disable-infobars")  # Disable infobars
        chrome_options.add_argument("--disable-notifications")
        # chrome_options.add_argument("--headless")
        driver = uc.Chrome(options=chrome_options)
        driver.maximize_window()
        # driver.set_window_size(1280, 720)
        return driver
    except Exception as e:
        logger.error(f"Failed to get chrome driver {str(e)}")
        raise e


def get_chrome_driver(browser_arguments=None, exp_arguments=None):
    """
    Fetch chrome driver and set download path for chrome
    Returns chrome driver
    """
    if exp_arguments is None:
        exp_arguments = {}
    if browser_arguments is None:
        browser_arguments = []
    try:
        options = webdriver.ChromeOptions()
        for br_args in browser_arguments:
            options.add_argument('ignore-certificate-errors')
            options.add_experimental_option("detach", True)

        for prefs, values in exp_arguments.items():
            options.add_experimental_option(prefs, values)

        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
        driver.maximize_window()
        # driver.set_window_size(1280, 720)
        return driver
    except Exception as error:
        logger.error(f"Failed to get chrome driver {str(error)}")
        raise error
