import pandas as pd
import re
import xlwings as xw
from excelFileObject import *

#TODO's: Format sheets, add stock data, find more information for company summary page, format company summary page, reorder pages

def writeSecFilingsData(excelFile, filingInfoDataFrame):
    # Initilize a startCell variable to track where to input dataframe info
    startCell = "A1"

    # Group the DataFrame by the 'form' column
    grouped = filingInfoDataFrame.groupby('form')

    # Create a dictionary to store DataFrames for each form type
    formDfs = {formType: group for formType, group in grouped}

    for key in formDfs:
        # Reformat the column names for display purposes
        formDfs[key].columns = ["Report Date:", "SEC Form Type:", "URL To Form:"]

        # Add the data to the sheet
        excelFile.addDataFromCell("SEC Filing Links", formDfs[key], startCell)

        # Iterate startCell to input next dataframe 1 column to the right of previous
        startCell = updateCellString(startCell, 4, 0)

def writeCompanyFactsData(excelFileObject, companyFactsData):
    # Initialize a DataFrame to store the summary
    companyFactsSummaryDF = pd.DataFrame(columns=[
        "Taxonomy:", "Taxonomy Concept:", "Description:", "Data Units:", "Data Source Url:", "Sheet Name:", "Sheet Link:"
    ])

    # List to store rows of the summary data to append
    summaryData = []
    
    # Track counters for each taxonomy
    taxonomyCounters = {}
    
    for taxonomy in companyFactsData:
        taxonomyCounters[taxonomy] = 0  # Initialize the counter for the taxonomy
        for taxonomyConcept in companyFactsData[taxonomy][:10]:  # TODO: Change indexing when code is done
            # Extract information
            sheetNameLabel = taxonomyConcept['label']
            description = taxonomyConcept['description']
            dataUnits = taxonomyConcept['units']
            dataSource = taxonomyConcept['source']
            data = taxonomyConcept['data']  # DataFrame containing the actual data

            # Increment the counter for this taxonomy
            taxonomyCounters[taxonomy] += 1

            # Generate the sheet name
            conceptNumber = taxonomyCounters[taxonomy]
            sheetName = f"{taxonomy}Sheet{conceptNumber}"
            
            # Add a new sheet for this taxonomy concept
            excelFileObject.addSheetWithData(sheetName, data)

            # Add a link to the summary sheet in the taxonomy concept sheet
            cellsToAdd = ["J1", "J2"]
            dataInCells = ["Link to Summary Sheet", createSheetHyperlink("Company SEC Data Summary")]
            excelFileObject.addCellToSheet(sheetName, cellsToAdd, dataInCells)
            
            # Append summary info to summary_data list
            summaryData.append({
                "Taxonomy": taxonomy,
                "Taxonomy Concept": sheetNameLabel,
                "Description": description,
                "Data Units": dataUnits,
                "Data Source Url": dataSource,
                "Sheet Name": sheetName,
                "Sheet Link": createSheetHyperlink(sheetName)
            })
    
    # Convert the list to a DataFrame and add it to the Excel file
    companyFactsSummaryDF = pd.DataFrame(summaryData)
    excelFileObject.addSheetWithData("Company SEC Data Summary", companyFactsSummaryDF)

def createSheetHyperlink(sheetName):
    """
    Creates a hyperlink formula for linking to a specific sheet within the same Excel workbook.
    
    The function checks if the sheet name contains special characters or spaces, 
    and formats the hyperlink formula accordingly.
    
    Args:
        sheet_name (str): The name of the sheet to link to.
        
    Returns:
        str: The Excel HYPERLINK formula as a string.
    
    Example:
        >>> create_hyperlink("us-gaapSheet9")
        '=HYPERLINK("#us-gaapSheet9!A1", "us-gaapSheet9")'
        
        >>> create_hyperlink("Sales Data 2024")
        '=HYPERLINK("#\'Sales Data 2024\'!A1", "Sales Data 2024")'
    """
    
    # Check if the sheet name contains spaces or special characters (anything other than letters, numbers, and underscores)
    if re.search(r'[^A-Za-z0-9_]', sheetName):
        # If special characters or spaces exist, enclose the sheet name in single quotes
        sheetName = "'" + sheetName + "'"  # Wrap the sheet name with single quotes
        
        # Now create the hyperlink formula with the sheet name in quotes
        hyperlinkFormula = f'=HYPERLINK("#{sheetName}!A1", "{sheetName[1:-1]}")'  # Remove quotes in the display part
    else:
        # If no special characters or spaces, use the sheet name directly
        hyperlinkFormula = f'=HYPERLINK("#{sheetName}!A1", "{sheetName}")'
    
    return hyperlinkFormula