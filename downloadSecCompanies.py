"""
SEC Company Listings Downloader

This script provides functionality to download and parse a JSON file containing
company listings maintained by the SEC. The data includes each company's CIK (Central Index Key),
ticker symbol, and name. The file is hosted and periodically updated by the SEC.

Key Features:
- Fetches a JSON file from the SEC containing details of all companies in their database.
- Extracts and returns the company data in a structured dictionary format.

Structure of the JSON Data:
- The JSON object contains key-value pairs where:
    Key: A unique company identifier.
    Value: A nested dictionary with the following fields:
        - "cik_str": The CIK number as a string.
        - "ticker": The company's stock ticker symbol as a string.
        - "title": The company's name as a string.

Dependencies:
- `requests`: For making HTTP requests to the SEC server.

Usage Example:
1. Call `downloadSecCompanies()` to fetch the latest company listings.
2. The function returns a dictionary with company details if successful, or `None` if the request fails.

Notes:
- Ensure you replace the placeholder email in the `User-Agent` header with your contact information, as per SEC guidelines.
- The SEC updates this file periodically. Check the SEC website for the latest information.

Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
"""

from makeRequest import makeRequest
from globalUrls import COMPANYLISTURL

def downloadSecCompanies():
    return makeRequest(COMPANYLISTURL)
