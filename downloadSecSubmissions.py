"""
File: donwloadSecSubmissions.py
Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
Date: 2024-12-27

Description:
------------
This script is designed to interact with the SEC EDGAR system to fetch, parse, and analyze 
company submission data. It includes functionality to send API requests, handle responses, 
and structure the data into descriptive and filing information for further processing.

Key Features:
-------------
- Fetches company submissions data from the SEC EDGAR system using the SEC API.
- Parses JSON responses into structured pandas DataFrames.
- Handles errors such as invalid JSON responses or failed HTTP requests.
- Allows for modular data handling via separate functions for description and filing data parsing.

Functions:
----------
1. `parseCompanyDescriptionInfo`: Extracts company descriptive information into a DataFrame.
2. `parseFilingInfo`: Parses filing details and constructs a DataFrame with additional metadata.
3. `parseCompanySubmissionsData`: Combines company description and filing info into DataFrames.
4. `bulkRequestCompanySubmissions`: Fetches and parses company submissions data via the SEC API.

Requirements:
-------------
- Python 3.7+
- pandas library
- requests library
- A valid User-Agent string for SEC API access (provided in the script).

Usage:
------
1. Ensure all dependencies are installed:
   pip install pandas requests

2. Run the script as part of a larger data pipeline or standalone:
   Example:
   companyDescriptionDF, filingInfoDF = bulkRequestCompanySubmissions("320193")

3. Use the parsed DataFrames for further analysis or storage.

Notes:
------
- Ensure that the User-Agent string complies with SEC's requirements.
- This script assumes the availability of a valid network connection for API requests.

"""

import requests
import time #REMOVE LATER
import pandas as pd
from makeRequest import makeRequest
from globalUrls import COMPANYSUBMISSIONSURL

def parseFilingInfo(filingInfo, cikNum):
    """
    Parses filing information and returns a DataFrame.

    Parameters:
    -----------
    filingInfo : dict
        The dictionary containing filing data, with lists as values for each key.
    cikNum : str
        The Central Index Key (CIK) number for the company.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the filing information with a 'dataSourceUrl' column.
    """
    # List of keys in filingInfo
    keys = [
        'accessionNumber', 'filingDate', 'reportDate', 'acceptanceDateTime', 
        'form', 'fileNumber', 'filmNumber', 'items', 'core_type', 'size', 
        'isXBRL', 'isInlineXBRL', 'primaryDocument', 'primaryDocDescription'
    ]
    
    # Extract values for each key
    filingData = {key: filingInfo.get(key, []) for key in keys}

    # Create a DataFrame from the parsed data
    df = createFilingInfoDataFrame(filingData, cikNum)

    # Replace empty strings with "N/A"
    df = df.replace("", "N/A")

    return df

def createFilingInfoDataFrame(filingData, cikNum):
    """
    Creates a DataFrame from the parsed filing data.

    Parameters:
    -----------
    filingData : dict
        A dictionary with keys as column names and values as lists of data.
    cikNum : str
        The Central Index Key (CIK) number for the company.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing filing information, including a 'dataSourceUrl' column.
    """
    # Convert the dictionary to a DataFrame
    df = pd.DataFrame(filingData)

    # Add the dataSourceUrl column
    df['dataSourceUrl'] = df.apply(
        lambda row: f'https://www.sec.gov/Archives/edgar/data/{cikNum}/{row["accessionNumber"].replace("-", "")}/{row["primaryDocument"]}',
        axis=1
    )

    # Remove unneeded columns from the dataframe
    df = df.drop(columns=[
        "accessionNumber", "filingDate", "acceptanceDateTime", "fileNumber", 
        "filmNumber", "items", "core_type", "size", "isXBRL", 
        "isInlineXBRL", "primaryDocument", "primaryDocDescription"
    ])

    return df    

def parseCompanyDescriptionInfo(companySubmissionData):
    """
    Parses the company submission data and returns a DataFrame with the desired information.

    Parameters:
    -----------
    companySubmissionData : dict
        The dictionary containing company submission data.

    Returns:
    --------
    pd.DataFrame
        A DataFrame containing the company's information with the following columns:
        - cik
        - entityType
        - sic
        - sicDescription
        - ownerOrg
        - insiderTransactionForOwner
        - insiderTransactionForIssuer
        - name
        - ticker
        - exchange
        - ein
        - description
        - website
        - investorWebsite
        - category
        - fiscalYearEnd
        - stateOfIncorporation
        - address
        - phone
    """
    data = {
        "cik": companySubmissionData.get("cik"),
        "entityType": companySubmissionData.get("entityType"),
        "sic": companySubmissionData.get("sic"),
        "sicDescription": companySubmissionData.get("sicDescription"),
        "ownerOrg": companySubmissionData.get("ownerOrg"),
        "insiderTransactionForOwner": companySubmissionData.get("insiderTransactionForOwnerExists"),
        "insiderTransactionForIssuer": companySubmissionData.get("insiderTransactionForIssuerExists"),
        "name": companySubmissionData.get("name"),
        "ticker": companySubmissionData.get("tickers", [None])[0],  # First ticker or None
        "exchange": companySubmissionData.get("exchanges", [None])[0],  # First exchange or None
        "ein": companySubmissionData.get("ein"),
        "description": companySubmissionData.get("description"),
        "website": companySubmissionData.get("website"),
        "investorWebsite": companySubmissionData.get("investorWebsite"),
        "category": companySubmissionData.get("category"),
        "fiscalYearEnd": companySubmissionData.get("fiscalYearEnd"),
        "stateOfIncorporation": companySubmissionData.get("stateOfIncorporation"),
        "address": companySubmissionData.get("addresses", {}).get("business"),  # Business address dictionary
        "phone": companySubmissionData.get("phone"),
    }

    # Convert the data dictionary to a DataFrame
    df = pd.DataFrame([data])

    # Combine address fields into a single string for readability, if present
    if isinstance(data["address"], dict):
        df["address"] = df["address"].apply(
            lambda addr: f"{addr.get('street1', '')}, {addr.get('city', '')}, {addr.get('stateOrCountry', '')} {addr.get('zipCode', '')}".strip()
            if addr else None
        )

    return df

def parseCompanySubmissionsData(companySubmissionData, cikNum):
    """
    Parses company submissions data to extract company description and filing information.

    This function processes the company submission data by splitting it into two separate 
    DataFrames: one containing the company's descriptive information and another containing 
    detailed filing information.

    Parameters:
    -----------
    companySubmissionData : dict
        A dictionary containing the company's submission data from the SEC EDGAR system.
        It includes details about the company and its recent filings.
    cikNum : str
        The Central Index Key (CIK) number for the company, used for constructing data source URLs.

    Returns:
    --------
    tuple
        A tuple containing two DataFrames:
        - companyDescriptionDataFrame: DataFrame with the company's descriptive information.
        - filingInfoDataFrame: DataFrame with details about the company's recent filings.

    Example:
    --------
    companyDescriptionDF, filingInfoDF = parseCompanySubmissionsData(companySubmissionData, "320193")
    """
    # Parse the company's descriptive information into a DataFrame
    companyDescriptionDataFrame = parseCompanyDescriptionInfo(companySubmissionData)

    # Parse the company's filing information into a DataFrame
    filingInfoDataFrame = parseFilingInfo(companySubmissionData['filings']['recent'], cikNum)

    # Return both DataFrames
    return companyDescriptionDataFrame, filingInfoDataFrame

def bulkRequestCompanySubmissions(cikNum):
    """
    Sends a request to the SEC API to fetch company submissions data for a given CIK number.

    This function retrieves data from the SEC EDGAR system using the provided CIK number, 
    processes the JSON response, and parses it into descriptive and filing information.

    Parameters:
    -----------
    cikNum : str
        The Central Index Key (CIK) number for the company. The number is zero-padded 
        to 10 digits to construct the SEC API request URL.

    Returns:
    --------
    tuple or None
        - A tuple containing two DataFrames:
          - companyDescriptionDataFrame: DataFrame with the company's descriptive information.
          - filingInfoDataFrame: DataFrame with details about the company's recent filings.
        - None if the request fails or the response cannot be parsed.

    Example:
    --------
    companyDescriptionDF, filingInfoDF = bulkRequestCompanySubmissions("320193")
    """
    # Make the request
    companySubmissionsData = makeRequest(COMPANYSUBMISSIONSURL, cikNum)

    # Parse the JSON data into descriptive and filing information DataFrames
    return parseCompanySubmissionsData(companySubmissionsData, cikNum)
