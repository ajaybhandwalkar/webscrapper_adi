import os
import shutil
import time
import traceback

import pandas as pd
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import Select
from chrome_instance import get_chrome_driver, web_wait_for_element, get_undetected_chrome_driver
from logger import init_logger

load_dotenv()
logger = init_logger()


class OpencorporateScrapper:

    def __init__(self, download_dir, file_name):
        self.download_dir = download_dir
        self.file_name = file_name

    @staticmethod
    def login(driver):
        driver.get(os.getenv("opencorporate_url"))
        time.sleep(1)
        web_wait_for_element(driver, By.XPATH, '//span[@itemprop="name" and text()="Login"]').click()
        time.sleep(1)
        web_wait_for_element(driver, By.XPATH, '//input[@placeholder="Email address"]').send_keys(
            os.getenv("opencorporate_user_name"))
        web_wait_for_element(driver, By.XPATH, '//input[@placeholder="Password"]').send_keys(
            os.getenv("opencorporate_password"))
        time.sleep(1)
        try:
            web_wait_for_element(driver, By.XPATH, '//button[@aria_label="Minimize"]').click()
        except:
            pass
        web_wait_for_element(driver, By.XPATH, '//button[text()="Sign in"]').click()

    def download_files(self, driver, url):
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        driver.get(url)
        web_wait_for_element(driver, By.ID, "MainContent_rdoByIdentification").click()
        time.sleep(2)
        web_wait_for_element(driver, By.ID, "MainContent_txtIdentificationNumber").send_keys(
            os.getenv("opencorporate_company_number"))
        driver.find_element(By.ID, "MainContent_btnSearch").click()
        web_wait_for_element(driver, By.XPATH, "//*[@id='MainContent_btnViewFilings']").click()
        driver.find_element(By.XPATH, '//*[@id="MainContent_grdSearchResults"]/tbody/tr[2]/td[5]/a')
        table = driver.find_element(By.XPATH, "//table[@id='MainContent_grdSearchResults']")
        rows = table.find_element(By.TAG_NAME, "tbody").find_elements(By.TAG_NAME, "tr")

        for row in rows:
            if len([f for f in os.listdir(self.company_dir) if os.path.isfile(os.path.join(self.company_dir, f))]) == 5:
                break
            tds = row.find_elements(By.TAG_NAME, "td")
            if tds:
                try:
                    name_of_filing = tds[0].text
                    year = tds[1].text
                    if os.path.exists(os.path.join(self.download_dir, "CorpSearchViewPDF.aspx")):
                        os.unlink(os.path.join(self.download_dir, "CorpSearchViewPDF.aspx"))
                        time.sleep(3)
                    tds[4].find_element(By.TAG_NAME, "a").click()
                    time.sleep(3)
                    shutil.copy(os.path.join(self.download_dir, "CorpSearchViewPDF.aspx"),
                                os.path.join(self.company_dir, name_of_filing.replace("/", " or ") + year + ".aspx"))
                except Exception as e:
                    logger.error(e)
        shutil.rmtree(self.download_dir)
        driver.close()
        driver.switch_to.window(driver.window_handles[0])

    @staticmethod
    def search_company(driver):
        web_wait_for_element(driver, By.XPATH, '//button[text()="Reject All"]').click()
        search_box_xpath = '//input[contains(@placeholder, "Search") and contains(@placeholder, "companies")]'
        web_wait_for_element(driver, By.XPATH, search_box_xpath).send_keys(os.getenv("opencorporate_company_number"))
        web_wait_for_element(driver, By.CSS_SELECTOR, '.fa.fa-search').click()
        search_result = web_wait_for_element(driver, By.ID, "companies")
        company_link = search_result.find_elements(By.TAG_NAME, "a")[1]
        company_link.click()

        # web_wait_for_element(driver, By.XPATH, '//button[text()="Reject All"]').click()
        # search_box_xpath = '//input[contains(@placeholder, "Search") and contains(@placeholder, "companies")]'
        # web_wait_for_element(driver, By.XPATH, search_box_xpath).send_keys("Analog devices")
        # select_element = web_wait_for_element(driver, By.NAME, "jurisdiction_code")
        # select = Select(select_element)
        # substring_to_find = "Massachusetts"
        # found = False
        # for option in select.options:
        #     if substring_to_find in option.text:
        #         select.select_by_visible_text(option.text)
        #         found = True
        #         break
        # if not found:
        #     logger.error("jurisdiction_code not found")
        # web_wait_for_element(driver, By.CSS_SELECTOR, '.fa.fa-search').click()

    def fetch_all_subsidiary(self, driver, see_all_subsidiary):
        driver.execute_script("window.open('');")
        driver.switch_to.window(driver.window_handles[1])
        time.sleep(1)
        driver.get(see_all_subsidiary)
        time.sleep(1)
        subsidiaries = {}
        pages = 0
        # table = driver.find_element(By.TAG_NAME, "table")
        try:
            while True:
                rows = driver.find_elements(By.XPATH, "//tr[not(.//span[@class='status label'])]")
                for row in rows:
                    try:
                        td = row.find_element(By.XPATH, ".//td[1]")
                        subsidiary = td.find_elements(By.TAG_NAME, "a")[1]
                        subsidiary_name = subsidiary.text
                        subsidiary_url = subsidiary.get_attribute("href")
                        subsidiaries[subsidiary_name] = subsidiary_url
                    except Exception:
                        pass
                pages += 1
                if "disabled" in web_wait_for_element(driver, By.CLASS_NAME, "pagination").find_elements(By.TAG_NAME, "li")[
                    -1].get_attribute("class"):
                    break
                web_wait_for_element(driver, By.CLASS_NAME, "pagination").find_elements(By.TAG_NAME, "li")[-1].find_element(
                    By.TAG_NAME, "a").click()
                time.sleep(1)
        except:
            pass
        driver.close()
        driver.switch_to.window(driver.window_handles[0])
        return subsidiaries

    def execute_script(self):  # async
        try:
            logger.info(f"Scraping data from {os.getenv("opencorporate_url")} for {os.getenv("company_name")}")
            driver = get_chrome_driver(['ignore-certificate-errors'], {
                'prefs': {'download.default_directory': self.download_dir, "download.prompt_for_download": False,
                          "download.directory_upgrade": True, "safebrowsing.enabled": True,
                          "plugins.always_open_pdf_externally": True}})

            # driver = get_undetected_chrome_driver()

            self.login(driver)
            self.search_company(driver)

            # source_div = driver.find_element(By.XPATH, "//div[@id='source']")
            # corp_element = source_div.find_element(By.XPATH, 'a[@href]')
            # if corp_element:
            #     corp_url = corp_element.get_attribute("href")
            #     self.download_files(driver, corp_url)

            subsidiary_row = web_wait_for_element(driver, By.XPATH,
                                                  '//div[@id="data-table-subsidiary_relationship_subject"]/ancestor::div[@class="row"]')
            rows = driver.find_elements(By.XPATH, '//div[@class="row"]')
            current_index = rows.index(subsidiary_row)
            subsidiaries = {}
            if current_index + 1 < len(rows):
                next_row_div = rows[current_index + 1]
                if "See all" in next_row_div.text:
                    see_all_subsidiary = next_row_div.find_element(By.TAG_NAME, "a").get_attribute("href")
                    subsidiaries = self.fetch_all_subsidiary(driver, see_all_subsidiary)
            else:
                logger.error("Failed to find See all subsidiaries link.")
            if subsidiaries:
                logger.info(subsidiaries)
                df = pd.DataFrame(list(subsidiaries.items()), columns=['Subsidiary Name', 'URL'])
                file_name = os.path.join(self.download_dir, self.file_name)
                if os.path.exists(file_name):
                    with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a", if_sheet_exists='overlay') as writer:
                        df.to_excel(writer, sheet_name="opencorporate_subsidiaries", index=False)
                else:
                    with pd.ExcelWriter(str(file_name), mode="w") as writer:
                        df.to_excel(writer, sheet_name="opencorporate_subsidiaries", index=False)
                logger.info(f"Data saved to {file_name}")
        except Exception as e:
            logger.error(f"Failed to scrap data from {os.getenv("opencorporate_url")} : {e}")
            logger.error(traceback.print_exc())
        finally:
            driver.quit()
