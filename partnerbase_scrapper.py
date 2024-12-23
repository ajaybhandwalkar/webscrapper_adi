import os
import time
import traceback
from urllib.parse import urljoin

import pandas as pd
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from logger import init_logger
from chrome_instance import get_undetected_chrome_driver, web_wait_for_element

load_dotenv()
logger = init_logger()


class PartnerbaseScrapper:
    def __init__(self, download_dir, file_name):
        self.download_dir = download_dir
        self.file_name = file_name
        self.cookies_rejected = False

    def search_company(self, driver, company_name=None) -> None:
        """
        Searches for a company on a webpage and attempts to click on the company's result if found.
        :param driver : The WebDriver instance used to interact with the web page
        :return: None
        """
        if not company_name:
            driver.get(os.getenv("partnerbase_url"))
            company_name = os.getenv("company_name")
        search_box = web_wait_for_element(driver, By.ID, "universal-search-box-input")
        if not search_box:
            raise f"Search box not found"
        time.sleep(4)
        if not self.cookies_rejected:
            reject_all_cookies = web_wait_for_element(driver, By.ID, "onetrust-reject-all-handler")
            if reject_all_cookies:
                driver.execute_script("arguments[0].click();", reject_all_cookies)
                time.sleep(2)
                self.cookies_rejected = True
        search_box.clear()
        search_box.send_keys(company_name)
        time.sleep(2)
        is_company_found = web_wait_for_element(driver, By.XPATH, f"//span[text()='{company_name}']")
        if is_company_found:
            try:
                is_company_found.click()
            except:
                driver.execute_script("arguments[0].click();", is_company_found)
        else:
            try:
                reject_all_cookies = driver.find_element(By.ID, "onetrust-reject-all-handler")
                if reject_all_cookies:
                    driver.execute_script("arguments[0].click();", reject_all_cookies)
                    time.sleep(2)
                    self.cookies_rejected = True
            except:
                pass
            search_box.clear()
            search_box.send_keys(company_name)
            time.sleep(2)
            is_company_found = web_wait_for_element(driver, By.XPATH, f"//span[text()='{company_name}']")
            if is_company_found:
                is_company_found.click()

    @staticmethod
    def get_profile_links(driver) -> dict:
        """
        Extracts and returns company profile links from a webpage.
        :param driver: The WebDriver instance used to interact with the web page
        :return: A dictionary mapping profile names to URLs.
        """
        profile_links = {}
        company_url_element = web_wait_for_element(driver, By.XPATH, "//a[img[@alt='link icon']]")
        if company_url_element:
            profile_links["Company"] = company_url_element.get_attribute("href")

        linkedin_url_element = web_wait_for_element(driver, By.XPATH, "//a[img[@alt='linkedin logo']]")
        if linkedin_url_element:
            profile_links["Linkedin"] = linkedin_url_element.get_attribute("href")

        twitter_url_element = web_wait_for_element(driver, By.XPATH, "//a[img[@alt='twitter logo']]")
        if twitter_url_element:
            profile_links["Twitter"] = twitter_url_element.get_attribute("href")

        crunchbase_url_element = web_wait_for_element(driver, By.XPATH, "//a[img[@alt='crunchbase logo']]")
        if crunchbase_url_element:
            profile_links["Crunchbase"] = crunchbase_url_element.get_attribute("href")

        return profile_links

    @staticmethod
    def fetch_general_info(general_info_section_element) -> dict:
        """
        Extracts and returns a dictionary of general information from General Information HTML section
        :param general_info_section_element: undetected_chromedriver.webelement.WebElement
        :return: A dictionary of labels and values. Includes a URL if present in the last item.

        """
        general_info = {}
        general_info_section = BeautifulSoup(general_info_section_element.get_attribute("outerHTML"), 'html.parser')
        general_info_li_tags = general_info_section.find_all('li', class_='c-info-item')
        for li in general_info_li_tags:
            label = li.find('label').get_text(strip=True)
            value = li.find('p') or li.find('div') or li.find('ul') or li.find('span')
            if value:
                if value.name == 'ul':
                    value = value.find("li").get_text(strip=True)
                else:
                    value = value.get_text(strip=True)
                general_info[label] = value
        try:
            general_info[general_info_li_tags[-1].find('label').get_text(strip=True)] = urljoin(
                os.getenv("partnerbase_url"), general_info_li_tags[-1].find("a").get("href"))
        except AttributeError:
            pass

        return general_info

    @staticmethod
    def fetch_partnership_info(partnership_info_section_element) -> dict:
        """
        Extracts and returns a dictionary of partnership information from Partnership Information HTML section
        :param partnership_info_section_element: undetected_chromedriver.webelement.WebElement
        :return: A dictionary where the keys are labels and the values are the extracted information.
        """
        partnership_info = {}
        partnership_info_section = BeautifulSoup(partnership_info_section_element.get_attribute("outerHTML"),
                                                 'html.parser')
        partnership_info_li_tags = partnership_info_section.find('ul',
                                                                 {'aria-label': 'Partnership Info Items'}).find_all(
            'li')
        for item in partnership_info_li_tags:
            label_list = item.find_all(string=True)
            label = label_list[0].strip()
            value = label_list[-1].strip()
            partnership_info[label] = value
        return partnership_info

    @staticmethod
    def fetch_partners(partners_element, driver):
        partners_div = BeautifulSoup(partners_element.get_attribute("outerHTML"), 'html.parser')
        table = partners_div.find("table")
        thead = table.find("thead")
        # thead_list = [th.get_text(strip=True) for th in thead.find_all("th") if th.get_text(strip=True)]
        # load_more = 0
        time.sleep(1)
        while web_wait_for_element(driver, By.XPATH, "//button[text()='Load More']", 5).is_enabled(): # and load_more < 4:
            driver.execute_script("arguments[0].click();",
                                  driver.find_element(By.XPATH, "//button[text()='Load More']"))
            time.sleep(1)
            # load_more += 1
        tbody_element = web_wait_for_element(driver, By.XPATH, '//*[@id="partners"]//table/tbody')
        tbody = BeautifulSoup(tbody_element.get_attribute("outerHTML"), 'html.parser')
        rows = tbody.find_all("tr")
        partnerbase_url = os.getenv("partnerbase_url")
        # partner_details = {"Sr.No.": [], "Company": [], "Partnerbase Score": [], "Partners": [], "Type": [],
        #                    "URL/link": []}
        partner_details = []

        for index, row in enumerate(rows):
            try:
                td = row.find_all("td")
                company_name = td[0].get_text(strip=True).split("View Company")[0]
                partner_link = td[0].find("a").get("href")
                partnerbase_score = td[1].get_text(strip=True)
                partners = td[2].get_text(strip=True)
                type = td[3].get_text(strip=True)
                if company_name and partner_link and partnerbase_score and partners and type:
                    # partner_details["Sr.No."].append(index + 1)
                    # partner_details["Company"].append(company_name)
                    # partner_details["Partnerbase Score"].append(partnerbase_score)
                    # partner_details["Partners"].append(partners)
                    # partner_details["Type"].append(type)
                    # partner_details["URL/link"].append(urljoin(partnerbase_url, partner_link))
                    partner_details.append((company_name, partnerbase_score, partners, type,
                                            urljoin(partnerbase_url, partner_link)))
            except Exception:
                pass
        return partner_details

    @staticmethod
    def create_sectioned_df(title, data_dict) -> pd.DataFrame:
        section_df = pd.DataFrame(list(data_dict.items()))
        title_df = pd.DataFrame([[title, '']])
        blank_df = pd.DataFrame([['', '']])
        return pd.concat([title_df, section_df, blank_df], ignore_index=True)

    def export_to_excel(self, profile_links, general_info, partnership_info, partner_details) -> None:
        df_profile_links = self.create_sectioned_df('Profile Links', profile_links)
        df_general_info = self.create_sectioned_df('General Info', general_info)
        df_partnership_info = self.create_sectioned_df('Partnership Info', partnership_info)
        df_combined = pd.concat([df_profile_links, df_general_info, df_partnership_info], ignore_index=True)

        # partners_df = pd.DataFrame(partner_details)
        columns = ['Company', 'Partnerbase Score', 'Partners', 'Type', 'URL/link']
        partners_df = pd.DataFrame(partner_details, columns=columns)
        headers = pd.DataFrame([partners_df.columns], columns=partners_df.columns)
        if len(partners_df.columns) > 0:
            title = pd.DataFrame([["Partner Details"] + [""] * (len(partners_df.columns) - 1)],
                                 columns=partners_df.columns)
        else:
            title = pd.DataFrame([["Partner Details"] + [""] * (len(partners_df.columns) - 1)])
        partners_df = pd.concat([title, headers, partners_df], ignore_index=True)
        file_name = os.path.join(self.download_dir, self.file_name)
        if os.path.exists(file_name):
            with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a", if_sheet_exists='overlay') as writer:
                df_combined.to_excel(writer, sheet_name='partnerbase_partners', startrow=0, index=False, header=False)
                partners_df.to_excel(writer, sheet_name='partnerbase_partners', startrow=len(df_combined), index=False,
                                     header=False)
        else:
            with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="w") as writer:
                df_combined.to_excel(writer, sheet_name='partnerbase_partners', startrow=0, index=False, header=False)
                partners_df.to_excel(writer, sheet_name='partnerbase_partners', startrow=len(df_combined), index=False,
                                     header=False)
        logger.info(f"Data saved to {file_name}")

    def recursive_partners(self, driver, company_name, level):
        self.search_company(driver, company_name)
        partners_element = web_wait_for_element(driver, By.ID, "partners")
        if partners_element:
            partner_details = self.fetch_partners(partners_element, driver)
            if partner_details:
                file_name = os.path.join(self.download_dir, self.file_name)
                if not os.path.exists(file_name):
                    partner_details.insert(0, ('Company', 'Partnerbase Score', 'Partners', 'Type', 'URL/link'))
                    partners_df = pd.DataFrame(partner_details)
                    partners_df[5] = company_name
                    partners_df[6] = level
                    partners_df.iloc[0, 5] = str("Parent")
                    partners_df.iloc[0, 6] = str("Level")
                    with pd.ExcelWriter(str(file_name), mode="w") as writer:
                        partners_df.to_excel(writer, sheet_name="Partnerbase_Partners", index=False,
                                             header=False)
                    return partners_df[0].tolist()[1:]
                else:
                    partners_df = pd.DataFrame(partner_details)
                    partners_df[5] = company_name
                    partners_df[6] = level
                    start_row = len(pd.read_excel(file_name, sheet_name="Partnerbase_Partners")) + 1
                    with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a",
                                        if_sheet_exists="overlay") as writer:
                        partners_df.to_excel(writer, sheet_name="Partnerbase_Partners", index=False,
                                             header=False, startrow=start_row)
                    return partners_df[0].tolist()
            else:
                return []

    def execute_script(self):
        try:
            logger.info(f"Scraping data from {os.getenv("partnerbase_url")} for {os.getenv("company_name")}")
            driver = get_undetected_chrome_driver()
            self.search_company(driver)
            profile_links = self.get_profile_links(driver)
            general_info = {}
            general_info_section_element = web_wait_for_element(driver, By.XPATH,
                                                                "//section[@aria-labelledby='general-info']")
            if general_info_section_element:
                general_info = self.fetch_general_info(general_info_section_element)

            partnership_info = {}
            partnership_info_section_element = web_wait_for_element(driver, By.XPATH,
                                                                    "//section[@aria-labelledby='partnership-info-label']")
            if partnership_info_section_element:
                partnership_info = self.fetch_partnership_info(partnership_info_section_element)

            partner_details = {}
            partners_element = web_wait_for_element(driver, By.ID, "partners")
            if partners_element:
                partner_details = self.fetch_partners(partners_element, driver)

            logger.info(f"General information : {general_info}")
            logger.info(f"Partnership information : {partnership_info}")
            logger.info(f"Partner Details :{partner_details}")
            self.export_to_excel(profile_links, general_info, partnership_info, partner_details)
        except Exception as e:
            logger.error(f"Failed to scrap data from {os.getenv("partnerbase_url")} : {e}")
            logger.error(traceback.print_exc())
        finally:
            driver.quit()
