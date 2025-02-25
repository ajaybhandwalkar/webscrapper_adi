import os
from yahooquery import search
import yfinance as yf
import pandas as pd
from openpyxl import load_workbook, Workbook
from logger import init_logger
from wb_utils import check_and_copy_workbook as update_sheet

logger = init_logger()


def get_ticker_from_company_name(company_name):
    """
    This function searches for the ticker symbol given a company name
    using Yahoo's search functionality provided by yahooquery.
    """
    try:
        result = search(company_name)
        if result and 'quotes' in result and len(result['quotes']) > 0:
            ticker = result['quotes'][0]['symbol']
            return ticker
        else:
            return None
    except Exception as e:
        return None


def get_company_risk_info(ticker, company_name):
    """
    Given a ticker, extract the company's risk-related financial data using yfinance.
    """
    company = yf.Ticker(ticker)

    try:
        info = company.info
        beta = info.get('beta', 'N/A')  # Volatility compared to the market
        debt_to_equity = info.get('debtToEquity', 'N/A')  # Leverage indicator
        quick_ratio = info.get('quickRatio', 'N/A')  # Liquidity indicator
        current_ratio = info.get('currentRatio', 'N/A')  # Liquidity indicator
        total_debt = info.get('totalDebt', 'N/A')  # Company's debt
        enterprise_value = info.get('enterpriseValue', 'N/A')  # Company's total valuation
        address1 = info.get('address1', 'N/A')
        address2 = info.get('address2', '')
        city = info.get('city', 'N/A')
        country = info.get('country', 'N/A')
        phone_no = info.get('phone', 'N/A')
        website = info.get('website', 'N/A')
        summary = info.get('longBusinessSummary', 'N/A')
        officers = info.get('companyOfficers', 'N/A')
        currency = info.get('currency', 'N/A')
        auditRisk = info.get('auditRisk', 'N/A')
        boardRisk = info.get('boardRisk', 'N/A')
        compensationRisk = info.get('compensationRisk', 'N/A')
        shareHolderRightsRisk = info.get('shareHolderRightsRisk', 'N/A')
        overallRisk = info.get('overallRisk', 'N/A')
        Name = company_name + ' ' + 'finacial Risk'
        officers = list(
            map(lambda x: {**{k if k != 'name' else 'Name': v for k, v in x.items()}, "Parent": company_name,
                           "Relationship": "officials"}, officers))

        risk_info = {
            "Name": Name,
            "Beta": beta,
            "Debt to Equity Ratio": debt_to_equity,
            "Quick Ratio": quick_ratio,
            "Current Ratio": current_ratio,
            "Total Debt": total_debt,
            "Enterprise Value": enterprise_value,
            "Address": address1 + ' ' + address2 + ' ' + city,
            "Country": country,
            "website": website,
            "Phone No": phone_no,
            "Summary": summary,
            "currency": currency,
            "Audit Risk": auditRisk,
            "Board Risk": boardRisk,
            "Compensation Risk": compensationRisk,
            "ShareHolderRights Risk": shareHolderRightsRisk,
            "Overall Risk": overallRisk,
            "Parent": company_name,
            "Relationship": 'Finacial Risk'
        },
        return risk_info, officers

    except Exception as e:
        return f"Error fetching data: {e}", None


def get_finca(company_name):
    ticker = get_ticker_from_company_name(company_name)
    file = company_name.replace(' ', '_')
    if ticker:
        logger.info(f"Ticker for {company_name}: {ticker}")
        risk_info, officers = get_company_risk_info(ticker, company_name)
        dic = {key: [d.get(key, 'N/A') for d in officers] for key in officers[0]}
        dic.pop('maxAge', None)
        df1 = pd.DataFrame(risk_info)
        file_1 = file + "_" + 'yfinrisk.xlsx'
        df1.to_excel(file_1)
        df2 = pd.DataFrame(dic)
        file_2 = file + "_" + 'yofficers_details.xlsx'
        df2.to_excel(file_2)

        update_sheet(existing_workbook_path=file_1, sheet_name_to_copy='yfRisk')

        update_sheet(existing_workbook_path=file_2, sheet_name_to_copy='yf_officials')
    else:
        logger.info(f"Could not find a ticker for the company '{company_name}'. Please try another name.")


if __name__ == "__main__":
    # company_name = input("Enter the company name: ")
    company_name = 'Analog Devices'
    ticker = get_ticker_from_company_name(company_name)

    if ticker:
        logger.info(f"Ticker for {company_name}: {ticker}")
        risk_info, officers = get_company_risk_info(ticker, company_name)
        dic = {key: [d.get(key, 'N/A') for d in officers] for key in officers[0]}
        dic.pop('maxAge', None)
        df1 = pd.DataFrame(risk_info)

        df1.to_excel('ADI_fin_risk.xlsx')
        df2 = pd.DataFrame(dic)
        df2.to_excel('officers_details.xlsx')

    else:
        logger.info(f"Could not find a ticker for the company '{company_name}'. Please try another name.")
