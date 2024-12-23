import os

from orbis_scrapper import Orbis
from chrome_instance import get_undetected_chrome_driver
from main import get_download_dir
from partnerbase_scrapper import PartnerbaseScrapper


class MoodysShareholders:
    def __init__(self):
        self.orbis_obj = Orbis(get_download_dir(), r"Moody's_Shareholders.xlsx")

    def get_all_suppliers(self, driver, company_name, processed=None, level=0, max_levels=2):
        if processed is None:
            processed = set()
        if company_name in processed or level >= max_levels:
            return []

        processed.add(company_name)
        suppliers = self.orbis_obj.recursive_shareholders(driver, company_name, level+1)
        all_suppliers = []

        for supplier in suppliers:
            all_suppliers.append(supplier)
            all_suppliers.extend(self.get_all_suppliers(driver, supplier, processed, level + 1, max_levels))

        return all_suppliers

    def execute_script(self):
        driver = get_undetected_chrome_driver()
        self.orbis_obj.login(driver)
        all_suppliers_list = self.get_all_suppliers(driver, os.getenv("company_name"))


class PartnerbasePartners:
    def __init__(self):
        self.partnerbase_obj = PartnerbaseScrapper(get_download_dir(), r"Partnerbase_Partners.xlsx")

    # def get_all_partners(self, driver, company_name, processed=None, level=0, max_levels=2):
    #     if processed is None:
    #         processed = set()
    #     if company_name in processed or level >= max_levels:
    #         return []
    #
    #     processed.add(company_name)
    #     partners = self.partnerbase_obj.recursive_partners(driver, company_name, level+1)
    #     all_suppliers = []
    #
    #     for partner in partners:
    #         all_suppliers.append(partner)
    #         all_suppliers.extend(self.get_all_partners(driver, partner, processed, level + 1, max_levels))
    #
    #     return all_suppliers

    def get_all_partners(self, driver, company_name, processed=None, level=0, max_levels=2):
        if processed is None:
            processed = set()

        # Base condition: avoid infinite recursion or exceeding max levels
        if company_name in processed or level >= max_levels:
            return []

        # Mark the current company as processed
        processed.add(company_name)

        try:
            # Fetch the partners of the current company
            partners = self.partnerbase_obj.recursive_partners(driver, company_name, level + 1)
        except Exception as e:
            print(f"Error fetching partners for {company_name}: {e}")
            return []

        all_suppliers = []

        for partner in partners:
            # Add partner if it's not already processed
            if partner not in processed:
                all_suppliers.append(partner)
                # Recursively get all partners of this partner, but do not process already processed partners
                new_partners = self.get_all_partners(driver, partner, processed, level + 1, max_levels)

                # Extend only the new partners that have not been processed already
                all_suppliers.extend([p for p in new_partners if p not in processed])

        # Optionally ensure all suppliers are unique
        all_suppliers = list(set(all_suppliers))

        return all_suppliers

    def execute_script(self):
        driver = get_undetected_chrome_driver()
        driver.get(os.getenv("partnerbase_url"))
        all_suppliers_list = self.get_all_partners(driver, os.getenv("company_name"))


if __name__ == '__main__':
    partnerbase_obj = PartnerbasePartners()
    partnerbase_obj.execute_script()
    # moodys_obj = MoodysShareholders()
    # moodys_obj.execute_script()
