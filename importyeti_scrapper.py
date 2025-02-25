import os
import time
import traceback

from logger import init_logger
import pandas as pd
import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
from googlesearch import search
from selenium.webdriver.common.by import By

from chrome_instance import get_undetected_chrome_driver, web_wait_for_element, get_chrome_driver

load_dotenv()
logger = init_logger()


class ImportyetiScrapper:
    def __init__(self, download_dir, file_name):
        self.download_dir = download_dir
        self.file_name = file_name

    @staticmethod
    def login(driver):
        try:
            time.sleep(2)
            signin = web_wait_for_element(driver, By.LINK_TEXT, "Sign in", 5)
            if signin:
                signin.click()
                time.sleep(1)
            web_wait_for_element(driver, By.ID, "email").send_keys(os.getenv("importyeti_user_name"))
            web_wait_for_element(driver, By.ID, "password").send_keys(os.getenv("importyeti_password"))
            # driver.find_element(By.XPATH, '//*[@id="headlessui-dialog-:r4:"]/div/div[2]/div/div[1]/form/button')
            time.sleep(1)
            web_wait_for_element(driver, By.XPATH, "//button[normalize-space(text())='Sign In']").click()
        except:
            pass

    def get_all_company_and_supplier(self, driver):
        driver.get(os.getenv("importyeti_url"))
        try:
            driver.execute_script("arguments[0].click();",
                                  web_wait_for_element(driver, By.XPATH, '//button[text()="Sign up free"]'))
        except:
            driver.execute_script("arguments[0].click();",
                                  web_wait_for_element(driver, By.XPATH, '//button[text()="Login"]'))
        self.login(driver)
        time.sleep(2)
        try:
            search_box = driver.find_element(By.XPATH, '//*[@placeholder="Find Any Company\'s Suppliers"]')
        except Exception:
            driver.refresh()
            time.sleep(2)
            search_box = web_wait_for_element(driver, By.XPATH, '//*[@placeholder="Find Any Company\'s Suppliers"]', 5)
        time.sleep(1)
        search_box.send_keys(os.getenv("company_name"))
        time.sleep(1)
        web_wait_for_element(driver, By.XPATH, '//button[@aria-label="Search button"]').click()
        time.sleep(4)
        # table = driver.find_elements(By.XPATH, '//*[@id="headlessui-tabs-panel-:R39jttsklja:"]/div')  # dynamic id
        try:
            if driver.find_element(By.CLASS_NAME, 'max-w-3xl'):
                time.sleep(1)
                search_box = driver.find_element(By.XPATH, '//*[@placeholder="Find Any Company\'s Suppliers"]')
                time.sleep(1)
                search_box.clear()
                search_box.send_keys(os.getenv("company_name"))
                time.sleep(1)
                web_wait_for_element(driver, By.XPATH, '//button[@aria-label="Search button"]').click()
                time.sleep(2)
        except Exception:
            logger.info("Company search is complete")
        table = driver.find_elements(By.XPATH, "//*[contains(@id, 'headlessui-tabs-panel-')]/div")
        table.pop(0)
        company_dict = {}
        supplier_list = []
        try:
            for index, div in enumerate(range(len(table))):

                customer_type = table[div].find_element(By.CSS_SELECTOR, 'div.absolute').text
                anchor_tag = table[div].find_element(By.CSS_SELECTOR, 'a')
                company_name = anchor_tag.text
                if customer_type == "Company":
                    company_dict[company_name] = anchor_tag.get_attribute("href")
                else:
                    supplier_list.append(company_name)
        except Exception:
            pass
        return company_dict, supplier_list

    def get_suppliers_for_each_company(self, driver, company_dict):
        supplier_details = [(
            'Supplier Name', 'Supplier Websites', 'Supplier Country', 'Shipments',
            'HS Code', 'Product Description')]
        for key, value in company_dict.items():
            driver.get(value)
            time.sleep(2)
            # table = web_wait_for_element(driver, By.XPATH, "/html/body/div[1]/main/div/div/section[2]/div[2]/table")
            try:
                web_wait_for_element(driver, By.TAG_NAME, 'table')
            except Exception:
                self.login(driver)
                time.sleep(2)
            show_element = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/section[2]/div[4]/span")
            while show_element.text == 'Show More' and show_element.is_enabled():
                show_element.click()
                time.sleep(1)
                show_element = driver.find_element(By.XPATH, "/html/body/div[1]/main/div/div/section[2]/div[4]/span")
            table = driver.find_element(By.TAG_NAME, 'table')
            table_body = table.find_element(By.TAG_NAME, "tbody")
            rows = table_body.find_elements(By.TAG_NAME, "tr")
            for row in rows:
                td = row.find_element(By.TAG_NAME, "td")
                supplier_name = td.find_element(By.CSS_SELECTOR, 'a').text
                country = ", ".join([loc.text for loc in td.find_elements(By.CSS_SELECTOR, 'a')[1:]])
                url = td.find_element(By.CSS_SELECTOR, 'a').get_attribute("href")
                products = row.find_elements(By.TAG_NAME, "td")[-1].find_element(By.TAG_NAME, "p").text
                total_shipments = row.find_elements(By.TAG_NAME, "td")[2].text.split("\n")[0]
                hs_codes = tuple(
                    i.text for i in row.find_elements(By.TAG_NAME, "td")[3].find_elements(By.TAG_NAME, "a"))
                # address = None
                # try:
                #     driver.execute_script("window.open('');")
                #     driver.switch_to.window(driver.window_handles[1])
                #     driver.get(url)
                #     address = web_wait_for_element(driver, By.XPATH,
                #                                    "/html/body/div[1]/main/div/div/div[1]/div[2]").text
                # except:
                #     pass
                # finally:
                #     driver.close()
                #     driver.switch_to.window(driver.window_handles[0])

                # if "Suppliers" in temp_dict.keys():
                #     temp_dict["Suppliers"].append(
                #         {"name": supplier_name, "url": url, "country": country, "products": products})
                # else:
                #     temp_dict["Suppliers"] = [
                #         {"name": supplier_name, "url": url, "country": country, "products": products}]

                supplier_details.append(tuple([supplier_name, url, country, total_shipments, hs_codes, products]))
            df = pd.DataFrame(supplier_details)
            file_name = os.path.join(self.download_dir, self.file_name)
            if os.path.exists(file_name):
                with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a", if_sheet_exists='overlay') as writer:
                    df.to_excel(writer, sheet_name="importyeti_suppliers", index=False, header=False)
            else:
                with pd.ExcelWriter(str(file_name), mode="w") as writer:
                    df.to_excel(writer, sheet_name="importyeti_suppliers", index=False, header=False)
            logger.info(f"Data saved to {file_name}")
        return supplier_details

    @staticmethod
    def fetch_company_links(company_name, num_results=10):
        logger.info(f"Fetching urls for Supplier : {company_name}")
        query = company_name
        links = []
        try:
            for url in search(query, num_results=num_results):
                links.append(url)
        except Exception as e:
            logger.error(f"An error occurred: {e}")

        return links

    @staticmethod
    def extract_url(url):
        try:
            response = requests.get(url, timeout=10)
            if response.status_code == 200:
                soup = BeautifulSoup(response.text, 'html.parser')
                text = soup.get_text()
                return True
        except Exception as e:
            # logger.error(url, e)
            return False

    def execute_script(self):
        try:
            logger.info(f"Scraping data from {os.getenv("importyeti_url")} for {os.getenv("company_name")}")
            driver = get_undetected_chrome_driver()
            company_dict, supplier_list = self.get_all_company_and_supplier(driver)
            logger.info(f"company: {company_dict}")
            logger.info(f"supplier_list: {supplier_list}")
            company_to_find = {key: value for key, value in company_dict.items() if key == os.getenv("company_name")}
            supplier_details = self.get_suppliers_for_each_company(driver, company_to_find)
            logger.info(supplier_details)
            return supplier_details
            # driver.close()
            # supplier_urls = {}
            # for supplier in updated_company_dict["Analog Device"]["Suppliers"]:
            #     supplier_urls[supplier["name"]] = self.fetch_company_links(supplier["name"])
            #
            # logger.info("Validating supplier urls : ")
            # valid_supplier_urls = []
            # for key, value in supplier_urls.items():
            #     for url in value:
            #         if self.extract_url(url):
            #             valid_supplier_urls.append((key, url))
            #
            # valid_supplier_url_df = pd.DataFrame(valid_supplier_urls, columns=['Supplier', 'URL'])
            # valid_supplier_url_df['Supplier'] = valid_supplier_url_df['Supplier'].where(
            #     valid_supplier_url_df.duplicated('Supplier', keep='first') == False)
            # valid_supplier_url_df.to_csv("supplier_urls.csv", index=False)
            # logger.info("Valid URLS for suppliers saved to: supplier_urls.csv")

        except Exception as e:
            logger.error(f"Failed to scrap data from {os.getenv("importyeti_url")} : {e}")
            logger.error(traceback.print_exc())
            raise e
        finally:
            driver.close()
