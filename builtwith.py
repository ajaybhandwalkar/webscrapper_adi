import os
import re
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from bs4 import BeautifulSoup
chrome_options = Options()
import pandas as pd
from wb_utils import check_and_copy_workbook as update_sheet

def run(company):
    driver = webdriver.Chrome()
    url= 'https://builtwith.com/meta/'+company
    driver.get(url)

    soup = BeautifulSoup(driver.page_source,"html.parser")
    company_name = [str((soup.find_all('dd', class_="col-sm-8")[0].text)).split('\n')[0]]
    address = [str(driver.find_elements(By.TAG_NAME,'address')[0].text).replace('\n',' ')]
    if len(soup.find_all('div', class_="card-body small"))>=6:
        social_links= ((soup.find_all('div', class_="card-body small")[5].text).split('\n'))
        social_links=[value for value in social_links if value != '' and value != '  ']
    else:
        social_links = []
    tables = soup.find_all('table', class_="table table-sm small")
    if len(tables)>=1:
        table = tables[0].find('tbody')
        rows = table.find_all("tr")
        finacial_info={"date":[], "revennue":[], "operating_income":[], "net_income":[]}
        for row in rows:
            cols = row.find_all("td")
            date= cols[0].text
            revennue=str(cols[1].text)
            operating_income=str(cols[2].text)
            net_income=str(cols[3].text)
            finacial_info.get("date").append(date)
            finacial_info.get("revennue").append(revennue)
            finacial_info.get("operating_income").append(operating_income)
            finacial_info.get("net_income").append(net_income)
    else:
        finacial_info={}

    personal_tables = soup.find_all('table', class_="table table-sm")
    if len(personal_tables)>=1:
        table = personal_tables[0].find('tbody')
        rows = table.find_all("tr")
        persoanl_info={"Name":[], "desig":[], "cont":[]}
        for row in rows:
            cols = row.find_all("td")
            Name= cols[0].text
            desig= cols[2].text
            links = cols[3].find_all('a')
            cont = [col.attrs.get('href') for col in links]
            persoanl_info.get("Name").append(Name)
            persoanl_info.get("desig").append(desig)
            persoanl_info.get("cont").append(cont)
    else:
        persoanl_info={}

    df1 = pd.DataFrame({
    "company_name": company_name})
    df2=pd.DataFrame({
    "address": address})
    df3=pd.DataFrame({
    "social_links": social_links})
    df4 = pd.DataFrame(finacial_info)
    df5 = pd.DataFrame(persoanl_info)

    file_path=f"{company}_builtwith.xlsx"

    with pd.ExcelWriter(file_path, engine='xlsxwriter') as writer:
        start_row=0
        for df in [df1, df2, df3, df4,df5]:
            df.to_excel(writer, sheet_name='Sheet1', startrow=start_row, index=False)

            start_row += len(df)+2

    driver.quit()
    update_sheet(existing_workbook_path=file_path, sheet_name_to_copy='builtwith_info')
    os.unlink(file_path)



if __name__ == "__main__":
    company= 'Analog.com'
    run(company)