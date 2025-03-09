"""
SEC Company Facts Data Fetcher

This script provides functionality to fetch, process, and correct company facts data from the SEC EDGAR API.
It is designed to parse complex JSON responses into a structured and usable format, enabling further analysis
of company filings and financial data.

Key Features:
- Fetch company facts data using the SEC API for a specified CIK (Central Index Key).
- Parse the JSON response to extract taxonomy, concept, and data unit details.
- Correct and normalize missing or inconsistent fields ('fy', 'fp', 'frame') in financial data.

Modules:
1. `bulkRequestCompanyFacts`: Fetches company facts data for a given CIK.
2. `parseCompanyFactsJSON`: Processes the main company facts JSON to extract relevant taxonomies and concepts.
3. `parseFactsDataJSON`: Parses facts data for each taxonomy and organizes it into structured dictionaries.
4. `updateFyAndFrameCols`: Corrects inconsistencies in the financial year, fiscal period, and frame columns.

Dependencies:
- `requests`: For making HTTP requests to the SEC API.
- `pandas`: For handling and processing tabular data.

Usage Example:
1. Call `bulkRequestCompanyFacts` with a valid CIK to fetch and process company facts data.
2. Processed data will be structured into dictionaries, with each taxonomy containing its respective concepts and details.

Notes:
- Ensure you replace the placeholder email in the `User-Agent` header with your contact information, as per SEC guidelines.
- Refer to the SEC EDGAR API documentation for details on data structures and additional endpoints.

Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
"""

import requests
import pandas as pd
from terminalUtils import clearTerminal
from makeRequest import makeRequest
from globalUrls import COMPANYFACTSURL

def bulkRequestCompanyFacts(cikNum):
    """
    Fetches company facts data from the SEC API for a given CIK (Central Index Key) number.

    Args:
        cikNum (str): The CIK number of the company to fetch data for.

    Returns:
        dict: Parsed data from the JSON response if successful, otherwise None.
    """
    # Send the request
    companyFactsData = makeRequest(COMPANYFACTSURL, cikNum)

    # Parse and return the fetched JSON data
    return parseCompanyFactsJSON(companyFactsData, cikNum)

def parseCompanyFactsJSON(companyFactsData, cikNum):
    """
    Parses the company facts data and extracts key information.

    Args:
        companyFactsData (dict): The raw JSON data fetched from the SEC API.
        cikNum (str): The CIK number of the company.

    Returns:
        conceptData (dict): A structured dictionary of the data in companyFactsData
    """
    # Extract the keys of the main JSON object
    mainKeys = companyFactsData.keys()

    # Extract the 'facts' section from the JSON data
    factsData = companyFactsData['facts']

    # Extract a sorted list of taxonomy keys (e.g., 'us-gaap', 'dei')
    factsKeys = sorted(factsData.keys())

    # Parse adn return the facts data
    return parseFactsDataJSON(factsData, factsKeys, cikNum)

def parseFactsDataJSON(factsData, factsKeys, cikNum):
    """
    Parses the facts data and organizes it into a structured dictionary.

    Args:
        factsData (dict): The 'facts' section of the company JSON data.
        factsKeys (list): Sorted list of taxonomy keys (e.g., 'us-gaap', 'dei').
        cikNum (str): The CIK number of the company.

    Returns:
        conceptData (dict): A structured dictionary of the data in factsData
    """
    # Dictionary to hold the parsed company data
    companyData = {}
    """
    Structure:
        {
            taxonomy: [ <- taxonomyDataList
                { <- conceptData Dictionary
                    "label": conceptLabel,<- conceptDataElements Dictionary
                    "description": conceptDescription,
                    "units": conceptUnits,
                    "source": dataSourceUrl,
                    "data": conceptDataFrame
                }
            ]
        }
    """

    # Iterate through each taxonomy (e.g., 'us-gaap', 'dei')
    for taxonomy in factsKeys:
        # List to store conceptData dictionaries
        taxonomyDataList = []

        # Get the data associated with the current taxonomy
        taxonomyData = factsData[taxonomy]

        # Extract and sort the concept keys for the current taxonomy
        sortedConcepts = sorted(taxonomyData.keys())

        # Iterate through each concept in the taxonomy
        for concept in sortedConcepts:  # Limit processing to the first concept (can be adjusted)
            # Dictionary to store the label, description, units, data source, and data for each element of taxonomy
            conceptData = {}

            # Extract concept details
            conceptLabel = taxonomyData[concept]['label']
            conceptDescription = taxonomyData[concept]['description']
            conceptUnitsList = list(taxonomyData[concept]['units'].keys())
            conceptUnits = conceptUnitsList[0]
            
            # Construct the data source URL
            dataSourceUrl = f'https://data.sec.gov/api/xbrl/companyConcept/CIK{cikNum.zfill(10)}/{taxonomy}/{concept}.json'

            # Create a DataFrame to store concept data
            conceptDataFrame = pd.DataFrame(columns=["end", "val", "accn", "fy", "fp", "form", "filed", "frame"])
            conceptDataList = taxonomyData[concept]['units'][conceptUnits]
            for dataElement in conceptDataList:
                conceptDataFrame.loc[len(conceptDataFrame)] = dataElement

            
            # Add extracted details to the dictionary
            conceptData['label'] = conceptLabel
            conceptData['description'] = conceptDescription
            conceptData['units'] = conceptUnits
            conceptData['source'] = dataSourceUrl

            conceptDataFrame = updateFyAndFrameCols(conceptDataFrame)
            conceptData['data'] = conceptDataFrame

            # Add the concept data to the taxonomy list
            taxonomyDataList.append(conceptData)
        
        # Add taxonomyDataList to the company dictionary
        companyData[taxonomy] = taxonomyDataList
    
    # Return the final structured data
    return companyData

def updateFyAndFrameCols(conceptDataFrame):
    """
    Corrects errors in the 'fy', 'fp', and 'frame' columns of the DataFrame based on specified rules.
    
    Parameters:
        conceptDataFrame (pd.DataFrame): The input DataFrame with potential errors.
    
    Returns:
        pd.DataFrame: The corrected DataFrame.
    """
    def correctRow(row):
        if (pd.isna(row['fp']) or row['fp'] == 'FY') and pd.isna(row['frame']):
            # Case 1: Both 'fp' and 'frame' are empty (or 'fp' is 'FY')
            row['fp'] = 'N/a'
            row['frame'] = f"CY{row['fy']}"
        
        elif pd.isna(row['frame']) and pd.notna(row['fp']) and row['fp'] != 'FY':
            # Case 2: 'frame' is empty, but 'fp' has a valid quarter
            row['frame'] = f"CY{row['fy']}{row['fp']}I"
        
        elif (pd.isna(row['fp']) or row['fp'] == 'FY') and pd.notna(row['frame']):
            if len(row['frame']) == 6:
                # Case 3a: 'frame' is of length 6, no quarter
                row['fp'] = 'N/A'
            elif len(row['frame']) >= 9:
                # Case 3b: 'frame' is of length >= 9, has a quarter
                row['fp'] = row['frame'][6:8]
        
        return row

    # Apply corrections row-wise
    conceptDataFrame = conceptDataFrame.apply(correctRow, axis=1)
    return conceptDataFrame