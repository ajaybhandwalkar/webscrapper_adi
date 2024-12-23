import os
import time

from bs4 import BeautifulSoup
from dotenv import load_dotenv
from selenium.webdriver.common.by import By
from chrome_instance import web_wait_for_element, get_undetected_chrome_driver, web_wait_for_elements
from logger import init_logger
import pandas as pd
from selenium.webdriver.support.ui import Select
import traceback

load_dotenv()
logger = init_logger()


class Orbis:

    def __init__(self, download_dir, file_name):
        self.download_dir = download_dir
        self.file_name = file_name

    @staticmethod
    def login(driver):
        driver.get(os.getenv("orbis_url"))
        driver.find_element(By.ID, "user").send_keys(os.getenv("orbis_username"))
        driver.find_element(By.ID, "pw").send_keys(os.getenv("orbis_password"))
        driver.find_element(By.CLASS_NAME, "ok").click()
        # driver.find_element('xpath', '//img[@alt="Search"]').click()
        if web_wait_for_element(driver, 'xpath', '//input[@value="Restart"]'):
            driver.find_element(By.XPATH, '//input[@value="Restart"]').click()
        # for _ in range(5):
        #     ele = web_wait_for_element(driver, By.XPATH, '//div[@id="border-1a426bd6-5426-4be5-9466-12f65bd6aac0"]', 2)
        #     if ele:
        #         ele.click()
        #         logger.info("Moody's alert closed.")
        #         break
        #     time.sleep(1)

    @staticmethod
    def search_company(driver, company_name):
        web_wait_for_element(driver, 'xpath', '//img[@alt="Search"]').click()
        web_wait_for_element(driver, 'xpath', '//input[@placeholder="Find a company"]').send_keys(company_name)
        results = web_wait_for_element(driver, By.ID, "quicksearch-results", 15)
        rows = web_wait_for_element(results, By.TAG_NAME, "ul", 20).find_elements(By.TAG_NAME, "li")
        if not rows:
            logger.error(f"{os.getenv("company_name")} not found.")
            raise Exception
        rows[0].find_element(By.CLASS_NAME, "name").click()
        time.sleep(1)
        web_wait_for_element(driver, By.XPATH,
                             '//*[@id="resultsTable"]/tbody/tr/td[1]/div/table/tbody/tr/td[4]/span').click()

    @staticmethod
    def get_identifier_details(driver):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#IDENTIFIERS"]').click()
        identifiers = []
        identifier_table = web_wait_for_element(driver, By.XPATH,
                                                '//*[@id="main-content"]/div[2]/div/form/table/tbody/tr[1]/td/table/tbody/tr[1]/td/table/tbody/tr/td/table')
        id_rows = identifier_table.find_elements(By.TAG_NAME, "tr")
        for row in id_rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            identifiers.append((tds[0].text, tds[2].text))

        legal_entity_identifier = []
        legal_entity_identifier_table = web_wait_for_element(driver, By.XPATH,
                                                             '//*[@id="main-content"]/div[2]/div/form/table/tbody/tr[2]/td/table/tbody/tr[2]/td/table/tbody/tr/td/table')
        le_id_rows = legal_entity_identifier_table.find_elements(By.TAG_NAME, "tr")
        for row in le_id_rows:
            tds = row.find_elements(By.TAG_NAME, "td")
            legal_entity_identifier.append((tds[0].text, tds[2].text))
        return identifiers, legal_entity_identifier

    @staticmethod
    def get_country_profile_details(driver):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#COUNTRYPROFILE"]').click()
        time.sleep(1)
        country_profile_tables = web_wait_for_elements(driver, By.XPATH, '//table[@class="ETBL midgetHolder__table"]')
        table1 = country_profile_tables[0].find_elements(By.TAG_NAME, "tr")
        table2 = country_profile_tables[1].find_elements(By.TAG_NAME, "tr")
        country_profile = []
        for left_row, right_row in zip(table1, table2):
            data = [left_row.text]
            [data.append(td.text) for td in right_row.find_elements(By.TAG_NAME, "td")]
            country_profile.append(tuple(data))
        driver.find_element(By.XPATH, '//img[@data-qc-id="Report.AdditionalInformationArrow"]').click()
        additional_info_div = driver.find_element(By.CLASS_NAME, "pscRegisterSeparator")
        additional_info = []
        for row in additional_info_div.find_elements(By.TAG_NAME, "tr"):
            if row.text != ' ' and len(row.find_elements(By.XPATH, './td')) == 3:
                td = row.find_elements(By.TAG_NAME, "td")
                additional_info.append((td[0].text, td[2].text.replace('\n', '  ')))
        return country_profile, additional_info

    @staticmethod
    def get_risk_score(driver):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#RISKSCORES"]').click()
        score = web_wait_for_element(driver, By.XPATH, "//td[@class='score']").text
        date = web_wait_for_element(driver, By.XPATH, "//td[@class='fsChartdate']").text
        msg = web_wait_for_element(driver, By.XPATH,
                                   '//*[@id="main-content"]/div[2]/div/form/table[1]/tbody/tr[2]/td/table/tbody/tr/td[3]/table').text.replace(
            "\n", " ")
        return score + "/900", date, msg

    def get_corporate_group(self, driver):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#CORPORATEGROUP"]').click()
        table = web_wait_for_element(driver, By.XPATH,
                                     "//table[@id='Section_CORPORATEGROUP_CG_OwnershipTable' and @class='ETBL ownershipMargin corporate-group']")
        self.scroll_into_view(driver, [table])
        logger.info(web_wait_for_elements(table, By.TAG_NAME, "tr").__len__())

        def click_all(eles):
            for ele in eles:
                try:
                    ele.click()
                except Exception:
                    pass

        hie_levels = web_wait_for_elements(table, By.XPATH,
                                           '//a[@title="Hierarchy levels" and @aria-label="Hierarchy levels"]')
        if not hie_levels:
            hie_levels = web_wait_for_elements(table, By.XPATH,
                                               '//a[@title="Hierarchy levels" and @aria-label="Hierarchy levels"]')
        click_all(hie_levels)
        self.scroll_into_view(driver, hie_levels)
        levels_box = web_wait_for_element(table, By.XPATH,
                                          '//div[@class="unfoldLevel-dropdown submenu-list selected" and @style="display: block;"]')
        self.scroll_into_view(driver, [levels_box])
        apply_btn = web_wait_for_elements(levels_box, By.XPATH, '//li[text()="Apply"]')
        self.scroll_into_view(driver, apply_btn)
        levels = levels_box.find_elements(By.XPATH, "//li[@class='level']/label")
        levels_value = [i.text for i in levels]
        # max_index = max((i for i, level in enumerate(levels_value) if level),
        #                 key=lambda i: int(levels_value[i].split()[0]))
        max_index = max(range(len(levels_value)),
                        key=lambda i: int(levels_value[i].split()[0]) if levels_value[i] else float('-inf'))
        levels[max_index].click()
        click_all(apply_btn)
        time.sleep(5)

        table = web_wait_for_element(driver, By.XPATH,
                                     "//table[@id='Section_CORPORATEGROUP_CG_OwnershipTable' and @class='ETBL ownershipMargin corporate-group']")
        # rows = web_wait_for_elements(table, By.TAG_NAME, "tr")
        soup = BeautifulSoup(table.get_attribute("outerHTML"), 'html.parser')
        rows = soup.find_all('tr')
        corporate_group = [
            ("Name", "Country", "Ownership_Direct", "Ownership_Total", "Level_Of_Own", "Info_Source", "Info_Date")]

        for row in rows[5:-1]:
            # if len(row.text.split("\n")) != 2:
            #     continue
            # data = row.text.split("\n")[1].split(" ")
            # if len(data) == 6:
            #     corporate_group.append(
            #         (row.text.split("\n")[0], data[0], data[1], data[2], data[3], data[4], data[5]))

            data = row.get_text().strip().split('\n')
            if len(data) >= 8:
                corporate_group.append((data[0], data[-6], data[-5], data[-4], data[-3], data[-2], data[-1]))

        return corporate_group

    def get_shareholders(self, driver, company_name):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#SHAREHOLDERS"]').click()
        select_element = web_wait_for_element(driver, By.XPATH, '//select[@id="dropDownNrItems"]')
        self.scroll_into_view(driver, [select_element])
        time.sleep(1)
        select = Select(select_element)
        time.sleep(1)
        try:
            if int(web_wait_for_element(driver, By.XPATH, "//input[@id='PageIndex']").get_attribute("max")) > 4:
                try:
                    try:
                        select.select_by_index(3)
                    except:
                        try:
                            select_element = web_wait_for_element(driver, By.XPATH, '//select[@id="dropDownNrItems"]')
                            self.scroll_into_view(driver, [select_element])
                            select = Select(select_element)
                            select.select_by_value("100")
                        except:
                            select.select_by_visible_text("100")
                    time.sleep(4)
                except:
                    pass
            pages = int(web_wait_for_element(driver, By.XPATH, "//input[@id='PageIndex']").get_attribute("max"))
        except:
            try:
                pages = int(web_wait_for_element(driver, By.XPATH, "//input[@id='PageIndex']", 2).get_attribute("max"))
            except:
                pages = 1
        # if pages >= 1:
        #     pages = 1
        logger.info(f"Scrolling pages {pages}")
        if os.path.exists(os.path.join(self.download_dir, self.file_name)):
            if "moody's_shareholders" in pd.ExcelFile(os.path.join(self.download_dir, self.file_name)).sheet_names:
                current_shareholders = []
            else:
                current_shareholders = [
                    ("Name", "Country", "Type", "Ownership_Direct", "Ownership_Total", "Info_Source",
                     "Info_Date", "Operating_revenue", "No_of_employees", "Parent")]
        else:
            current_shareholders = [
                ("Name", "Country", "Type", "Ownership_Direct", "Ownership_Total", "Info_Source",
                 "Info_Date", "Operating_revenue", "No_of_employees", "Parent")]

        for page in range(pages):
            table = web_wait_for_element(driver, By.XPATH,
                                         '//table[@id="Section_SHAREHOLDERS_InLines_OwnershipTable" and @class="ETBL ownershipMargin ownership-table"]',
                                         30)
            soup = BeautifulSoup(table.get_attribute("outerHTML"), 'html.parser')
            rows = soup.find_all('tr')
            for row in rows[2:-1]:
                data = row.find_all('td')
                current_shareholders.append(tuple(
                    value.find('span').get("title") if index == 3
                    else value.get_text() for index, value in enumerate(data) if index not in [1, 4]
                ))
            try:
                if page == pages - 1:
                    break
                web_wait_for_element(driver, By.CLASS_NAME, "next").click()
                time.sleep(3)
            except:
                web_wait_for_element(driver, By.CLASS_NAME, "next").click()
                time.sleep(3)
        return current_shareholders

    def scroll_into_view(self, driver, eles: list):
        for ele in eles:
            try:
                driver.execute_script("arguments[0].scrollIntoView();", ele)
            except Exception:
                pass

    def recursive_shareholders(self, driver, company_name, level):
        try:
            self.search_company(driver, company_name)
            self.scroll_into_view(driver, [web_wait_for_element(driver, By.XPATH, '//a[@title="Corporate ownership"]')])
            driver.execute_script("arguments[0].click();",
                                  web_wait_for_element(driver, By.XPATH, '//a[@title="Corporate ownership"]'))
            current_shareholders = self.get_shareholders(driver, company_name)
            current_shareholders_df = pd.DataFrame(current_shareholders)
            current_shareholders_df[9] = company_name
            current_shareholders_df[10] = level
            file_name = os.path.join(self.download_dir, self.file_name)
            if os.path.exists(file_name):
                start_row = len(pd.read_excel(file_name, sheet_name="moody's_shareholders")) + 1
                with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a", if_sheet_exists="overlay") as writer:
                    current_shareholders_df.to_excel(writer, sheet_name="moody's_shareholders", index=False, header=False,
                                                     startrow=start_row)
                return current_shareholders_df[0].tolist()
            else:
                current_shareholders_df.iloc[0, 9] = "Parent"
                current_shareholders_df.iloc[0, 10] = "Level"
                with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="w") as writer:
                    current_shareholders_df.to_excel(writer, sheet_name="moody's_shareholders", index=False, header=False)
                return current_shareholders_df[0].tolist()[1:]
        except Exception as e:
            logger.info(f"Failed to get shareholders for {company_name}")
            return []


    def get_subsidiaries(self, driver):
        web_wait_for_element(driver, By.XPATH, '//a[@href="#SUBSIDIARIES"]').click()
        table = web_wait_for_element(driver, By.XPATH,
                                     '//table[@id="Section_SUBSIDIARIES_InLines_OwnershipTable" and @class="ETBL ownershipMargin ownership-table"]',
                                     30)
        if os.path.exists(os.path.join(self.download_dir, self.file_name)) and "moody's_subsidiaries" in pd.ExcelFile(
                os.path.join(self.download_dir, self.file_name)).sheet_names:
            current_subsidiaries = []
        else:
            current_subsidiaries = [
                ("Name", "Country", "Type", "Ownership_Direct", "Ownership_Total", "Info_Source",
                 "Info_Date", "Operating_revenue", "No_of_employees")]
        soup = BeautifulSoup(table.get_attribute("outerHTML"), 'html.parser')
        rows = soup.find_all('tr')
        for row in rows[2:-1]:
            try:
                data = row.find_all('td')
                try:
                    source = f"({data[8].text}) - " + data[8].find("span").get("title")
                except:
                    source = "-"
                current_subsidiaries.append((data[1].text, data[3].find("span").get("title"),
                                             data[4].find("span").get("title"), data[6].text, data[7].text, source,
                                             data[9].find("span").get("title"), data[10].text, data[11].text,
                                             data[12].text))

            except:
                pass
        return current_subsidiaries

    def execute_script(self):
        try:
            logger.info(f"Scraping data from {os.getenv("orbis_url")} for {os.getenv("company_name")}")
            driver = get_undetected_chrome_driver()
            self.login(driver)
            self.search_company(driver, os.getenv("company_name"))

            self.scroll_into_view(driver, [web_wait_for_element(driver, By.XPATH, '//a[@title="Corporate ownership"]')])
            driver.execute_script("arguments[0].click();",
                                  web_wait_for_element(driver, By.XPATH, '//a[@title="Corporate ownership"]'))

            corporate_group = self.get_corporate_group(driver)
            current_shareholders = self.get_shareholders(driver, os.getenv("company_name"))
            current_subsidiaries = self.get_subsidiaries(driver)
            current_shareholders_df = pd.DataFrame(current_shareholders)
            corporate_group_df = pd.DataFrame(corporate_group)
            current_subsidiaries_df = pd.DataFrame(current_subsidiaries)
            if not current_shareholders_df.empty:
                current_shareholders_df[9] = os.getenv("company_name")
                current_shareholders_df.iloc[0, 9] = "Parent"
            file_name = os.path.join(self.download_dir, self.file_name)

            if os.path.exists(file_name):
                with pd.ExcelWriter(str(file_name), engine='openpyxl', mode="a", if_sheet_exists='overlay') as writer:
                    current_shareholders_df.to_excel(writer, sheet_name="moody's_shareholders", index=False,
                                                     header=False)
                    corporate_group_df.to_excel(writer, sheet_name="moody's_corporate_group", index=False, header=False)
                    current_subsidiaries_df.to_excel(writer, sheet_name="moody's_subsidiaries", index=False,
                                                     header=False)
            else:
                with pd.ExcelWriter(str(file_name), mode="w") as writer:
                    current_shareholders_df.to_excel(writer, sheet_name="moody's_shareholders", index=False,
                                                     header=False)
                    corporate_group_df.to_excel(writer, sheet_name="moody's_corporate_group", index=False, header=False)
                    current_subsidiaries_df.to_excel(writer, sheet_name="moody's_subsidiaries", index=False,
                                                     header=False)
            logger.info(f"Data saved to {file_name}")
            driver.quit()
        except Exception as e:
            logger.error(f"Failed to scrap data from {os.getenv("orbis_url")} : {e}")
            logger.error(traceback.print_exc())


# web_wait_for_element(driver, By.XPATH, '//a[@title="Company profile"]').click()
# # identifiers, legal_entity_identifier = self.get_identifier_details(driver)
# # country_profile, additional_info = self.get_country_profile_details(driver)
# web_wait_for_element(driver, By.XPATH, '//a[@title="Company profile"]').click()
#
# web_wait_for_element(driver, By.XPATH, '//a[@title="Trade payment data"]').click()
# # score, date, msg = self.get_risk_score(driver)
# web_wait_for_element(driver, By.XPATH, '//a[@title="Trade payment data"]').click()

# # driver.execute_script("arguments[0].click();", web_wait_for_element(driver, By.XPATH, '//a[text()="Geographic footprint"]'))
# # driver.execute_script("arguments[0].scrollIntoView();", web_wait_for_element(driver, By.XPATH, "//td[text()='Filter by']"))
# # web_wait_for_element(driver, By.XPATH, '//div[@class="map display"]').screenshot("geographic_footprint.png")
