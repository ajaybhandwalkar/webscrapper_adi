from importyeti_scrapper import ImportyetiScrapper
from partnerbase_scrapper import PartnerbaseScrapper
from opencorporate_download_files import OpencorporateScrapper
import os
import shutil
# from importgen import run as importgenious_run
# from builtwith import builtwith_run
# from links import run as link_run
import asyncio
from concurrent.futures import ThreadPoolExecutor
from orbis_scrapper import Orbis
from chrome_instance import get_undetected_chrome_driver
#############
from risk_rating import get_finca
from ig_suppliers import process
from ig_importers import process2
from builtwith import run as builtwith_run


def get_download_dir():
    temp_dir = os.path.join(str(os.getcwd()), os.getenv("company_name"))
    # if os.path.exists(temp_dir):
    #     shutil.rmtree(temp_dir)
    # os.mkdir(temp_dir)
    if not os.path.exists(temp_dir):
        os.mkdir(temp_dir)
    return temp_dir


# async def main():
#     download_dir = get_download_dir()
#     importyeti_obj = ImportyetiScrapper(download_dir)
#     partnerbase_obj = PartnerbaseScrapper(download_dir)
#     opencorporate_obj = OpencorporateScrapper(download_dir)
#
#     with ThreadPoolExecutor() as executor:
#         asyncio.create_task(opencorporate_obj.execute_script())
#         await asyncio.get_event_loop().run_in_executor(executor, importyeti_obj.execute_script)
#         await asyncio.get_event_loop().run_in_executor(executor, partnerbase_obj.execute_script)


if __name__ == '__main__':
    download_dir = get_download_dir()
    file_name = "Nth Tier Mapping.xlsx"
    importyeti_obj = ImportyetiScrapper(download_dir, file_name)
    partnerbase_obj = PartnerbaseScrapper(download_dir, file_name)
    opencorporate_obj = OpencorporateScrapper(download_dir, file_name)
    orbis_obj = Orbis(download_dir, file_name)
    orbis_obj.execute_script()
    try:
        importyeti_obj.execute_script()
    except:
        try:
            importyeti_obj.execute_script()
        except:
            pass
    partnerbase_obj.execute_script()
    opencorporate_obj.execute_script()

    # Second Half Code
    company = os.getenv("company_name")
    website = os.getenv("website")
    process(company)
    process2(company)
    get_finca(company)
    builtwith_run(website)

    # asyncio.run(main())
