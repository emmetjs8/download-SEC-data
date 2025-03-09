from searchSecCompanies import mainSearch
from requestCompanyFacts import bulkRequestCompanyFacts
from downloadSecSubmissions import bulkRequestCompanySubmissions
from excelFileObject import FinancialExcelFile
from excelFileUtils import *
import time

# Find the company to download data for
title, ticker, cik = mainSearch()
print(f"Downloading SEC Data for {title}\n\tTicker: {ticker}\n\tCik: {cik}")
time.sleep(5)

# Download the SEC Data
if title:
    companyFactsData = bulkRequestCompanyFacts(cik)
    companyDescriptionDataFrame, filingInfoDataFrame = bulkRequestCompanySubmissions(cik)

# Upload data to an excel file
excelFileName = "test1.xlsx"
excelFile = FinancialExcelFile(excelFileName)

writeCompanyFactsData(excelFile, companyFactsData)
writeSecFilingsData(excelFile, filingInfoDataFrame)
excelFile.addSheetWithData("Company Summary", companyDescriptionDataFrame) # TODO: Update
excelFile.saveAndClose()