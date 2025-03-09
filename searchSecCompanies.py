"""
Company Search and Browsing System

This script provides functionality to search for companies in a dataset 
obtained from the SEC and allows users to browse or search for individual 
companies based on their ticker, title, or CIK (Central Index Key). 

The system provides two main features:
1. Searching for a single company by ticker, title, or CIK.
2. Browsing through a paginated list of all companies.

Functions in this file:
-----------------------
- mainSearch(): Entry point that prompts the user to either search for a single 
  company or browse all companies.
- searchCompany(): Allows the user to search for a company using the ticker, title, 
  or CIK index.
- browseAllCompanies(): Displays a paginated list of all companies and allows 
  the user to select a company for more details.
- displayCompanyTable(): Displays a paginated table of companies, allowing the user 
  to navigate through them.
- sortAllCompanies(): Sorts the companies alphabetically by title.
- createHashIndexes(): Creates index dictionaries for ticker, title, and CIK.
- downloadSecCompanies(): Downloads the dataset of companies from the SEC.

Dependencies:
-------------
- `tabulate` - For displaying the company data in a tabular format.
- `time` - For managing delays between user interactions.
- Other necessary standard Python libraries.

Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
"""

import time
from tabulate import tabulate
from terminalUtils import *
from downloadSecCompanies import *

###############################################
###############################################
# Main Search Function
###############################################
###############################################

def mainSearch():
    """
    Prompts the user to choose between searching for a single company or browsing all companies.
    Based on the user's input, it either calls the `searchCompany` function or the `browseAllCompanies` function.

    This function serves as the entry point for the user to search for a company or browse a list of companies 
    using different search criteria (ticker, title, or CIK).

    Parameters:
    -----------
    None

    Returns:
    --------
    tuple or None
        A tuple containing the title, ticker, and CIK of the selected company if a valid selection is made, 
        or None if no valid selection is made during the search or browsing process.
    """
    # Clear the initial screen
    clearTerminal()
    
    # Download the company data from the SEC and create indexes for faster lookup
    companyData = downloadSecCompanies()
    tickerIndex, titleIndex, cikIndex = createHashIndexes(companyData)

    # Prompt the user for their choice of search method (single company search or browsing all companies)
    choice = input("Do you want to:\n\t1. Search for a single company\n\t2. Browse all companies\nEnter 1 or 2: ").strip()
    clearTerminal()

    if choice == "1":
        # If the user chooses to search for a single company, call the searchCompany function
        return searchCompany(tickerIndex, titleIndex, cikIndex)
    
    elif choice == "2":
        # If the user chooses to browse all companies, call the browseAllCompanies function
        return browseAllCompanies(titleIndex, tickerIndex, cikIndex)
    
    else:
        # If the user enters an invalid choice, notify them and retry the search
        print("Invalid choice. Please enter 1 or 2.")
        time.sleep(5)
        clearTerminal()
        return mainSearch()  # Retry the selection process

###############################################
###############################################
# Create hash tables functions
###############################################
###############################################

def createHashIndexes(companyData):
    """
    Create index dictionaries for efficient lookup of company information.

    This function creates three index dictionaries from the input company data:
    - `tickerIndex` for searching by ticker (case-insensitive).
    - `titleIndex` for searching by company title (case-insensitive).
    - `cikIndex` for searching by CIK (Central Index Key).

    Parameters:
    -----------
    companyData : dict
        A dictionary where each key is a unique identifier, and each value is a dictionary
        containing company information, including 'ticker', 'title', and 'cik_str'.

    Returns:
    --------
    tuple
        - tickerIndex (dict): Keys are lowercase tickers, values are lists of dictionaries with 'cik_str' and 'title'.
        - titleIndex (dict): Keys are lowercase company titles, values are lists of dictionaries with 'cik_str' and 'ticker'.
        - cikIndex (dict): Keys are CIK strings, values are lists of dictionaries with 'ticker' and 'title'.
    """
    tickerIndex = {}
    titleIndex = {}
    cikIndex = {}

    for key, company in companyData.items():
        # Index by ticker (case-insensitive, allowing duplicates)
        ticker = company['ticker'].lower()
        tickerIndex.setdefault(ticker, []).append({'cik_str': company['cik_str'], 'title': company['title']})

        # Index by title (case-insensitive, allowing duplicates)
        title = company['title'].lower()
        titleIndex.setdefault(title, []).append({'cik_str': company['cik_str'], 'ticker': company['ticker']})

        # Index by CIK (converted to string, allowing duplicates)
        cik_str = str(company['cik_str'])
        cikIndex.setdefault(cik_str, []).append({'ticker': company['ticker'], 'title': company['title']})

    return tickerIndex, titleIndex, cikIndex

###############################################
###############################################
# Search hash table functions
###############################################
###############################################

def searchByTitle(titleIndex, titleTarget):
    """
    Search for companies by their title.

    Parameters:
    -----------
    titleIndex : dict
        The index dictionary for company titles created by `createHashIndexes`.
    titleTarget : str
        The title to search for (case-insensitive).

    Returns:
    --------
    list or None
        A list of matching companies, or None if no match is found.
    """
    return titleIndex.get(titleTarget.lower(), None)

def searchByTicker(tickerIndex, tickerTarget):
    """
    Search for companies by their ticker.

    Parameters:
    -----------
    tickerIndex : dict
        The index dictionary for company tickers created by `createHashIndexes`.
    tickerTarget : str
        The ticker to search for (case-insensitive).

    Returns:
    --------
    list or None
        A list of matching companies, or None if no match is found.
    """
    return tickerIndex.get(tickerTarget.lower(), None)

def searchByCik(cikIndex, cikTarget):
    """
    Search for companies by their CIK (Central Index Key).

    Parameters:
    -----------
    cikIndex : dict
        The index dictionary for CIKs created by `createHashIndexes`.
    cikTarget : str
        The CIK to search for.

    Returns:
    --------
    list or None
        A list of matching companies, or None if no match is found.
    """
    return cikIndex.get(cikTarget, None)

###############################################
###############################################
# Search single company functions
###############################################
###############################################

def searchCompany(tickerIndex, titleIndex, cikIndex):
    """
    Prompts the user to input a company title, ticker, or CIK, and determines 
    the type of input. It searches the appropriate hash table based on the input 
    and returns the result. The search supports partial matching for titles.

    Parameters:
    -----------
    tickerIndex : dict
        The index dictionary for tickers created by `createHashIndexes`.
    titleIndex : dict
        The index dictionary for titles created by `createHashIndexes`.
    cikIndex : dict
        The index dictionary for CIKs created by `createHashIndexes`.

    Returns:
    --------
    tuple or None
        A tuple containing the title, ticker, and cik of the selected company, 
        or None if no match is found or if the user cancels the search.
    """
    userInput = input("Enter a company title, ticker, or CIK: ").strip()

    # Determine input type and search for the company
    if userInput.isdigit():
        # Likely a CIK (all digits)
        print("Searching by CIK...")
        result = searchByCik(cikIndex, userInput)
        parsedResults = parseSearchResults(result, userInput)
    elif userInput.isalpha() or userInput.isalnum():
        # Could be a ticker (all alphanumeric)
        print("Searching by ticker...")
        result = searchByTicker(tickerIndex, userInput.lower())
        
        # If no result is found, fallback to searching as a title
        if not result:
            print("No ticker found, searching by title...")
            result = searchByTitle(titleIndex, userInput.lower(), partial=True)
        
        parsedResults = parseSearchResults(result, userInput)
    else:
        # Likely a title search (contains spaces or special characters)
        print("Searching by title...")
        result = searchByTitle(titleIndex, userInput.lower(), partial=True)
        parsedResults = parseSearchResults(result, userInput)
    
    # Handle parsed results (no results, multiple results, or single result)
    return handleSearchResults(parsedResults, tickerIndex, titleIndex, cikIndex, userInput)

def handleSearchResults(parsedResults, tickerIndex, titleIndex, cikIndex, userInput):
    """
    Handles the results of a company search. It takes appropriate actions based 
    on the number of results returned.
    
    - If no company is found, it prompts the user to search again.
    - If multiple companies are found, it allows the user to select one.
    - If exactly one company is found, it returns the company's details.

    Parameters:
    -----------
    parsedResults : tuple
        A tuple containing parsed search results, such as (titles, tickers, ciks).
        If no result is found, this will be None.
    tickerIndex : dict
        The index dictionary for tickers used for re-searching when needed.
    titleIndex : dict
        The index dictionary for titles used for re-searching when needed.
    cikIndex : dict
        The index dictionary for CIKs used for re-searching when needed.
    userInput : str
        The original user input used for searching, used to fill missing search fields.

    Returns:
    --------
    tuple or None
        A tuple containing the title, ticker, and cik of the selected company, 
        or None if no valid selection is made.
    """
    # If no results are found, prompt the user to try again
    if not parsedResults:
        print(f"No companies found for '{userInput}'. Please try again.")
        time.sleep(5)
        clearTerminal()
        return searchCompany(tickerIndex, titleIndex, cikIndex)  # Recursively ask the user to search again

    # Handle the case where only one result is returned
    elif isinstance(parsedResults[0], str) and len(parsedResults) == 3:
        clearTerminal()
        return parsedResults[0], parsedResults[1], parsedResults[2]

    # If multiple companies are found, prompt the user to select one
    elif len(parsedResults[0]) > 1:
        print("Multiple companies found. Please choose one by entering the corresponding number:")
        for idx in range(len(parsedResults[0])):
            print(f"{idx+1}. Title: {parsedResults[0][idx]}, Ticker: {parsedResults[1][idx]}, CIK: {parsedResults[2][idx]}")
        
        try:
            # Prompt user for selection
            selection = int(input("Enter the number of the company you want to select: "))
            if 1 <= selection <= len(parsedResults[0]):
                # Return the selected company info
                clearTerminal()
                return parsedResults[0][selection - 1], parsedResults[1][selection - 1], parsedResults[2][selection - 1]
            else:
                # Invalid selection, retry the search
                print("Invalid selection. Please try again.")
                time.sleep(5)
                clearTerminal()
                return handleSearchResults(parsedResults, userInput)  # Retry on invalid input
        except ValueError:
            # Handle non-integer input
            print("Invalid input. Please enter a valid number.")
            time.sleep(5)
            clearTerminal()
            return handleSearchResults(parsedResults, userInput)  # Retry on invalid input

def searchByTitle(titleIndex, titleTarget, partial=False):
    """
    Searches for companies by title. Supports exact or partial matching of titles.

    Parameters:
    -----------
    titleIndex : dict
        The index dictionary for titles created by `createHashIndexes`.
    titleTarget : str
        The title or substring to search for in company titles.
    partial : bool
        If True, allows partial matching (i.e., titleTarget is a substring of company titles).
        If False, requires an exact match.

    Returns:
    --------
    list or None
        A list of dictionaries containing company information (ticker, title, cik_str) 
        for companies that match the title search criteria. Returns None if no match is found.
    """
    result = []

    for title, companies in titleIndex.items():
        if partial:
            # Check if titleTarget is a substring of the company's title (case-insensitive)
            if titleTarget in title.lower():
                result.extend(companies)
        else:
            # Exact match search (case-insensitive)
            if titleTarget == title.lower():
                result.extend(companies)

    return result if result else None

def parseSearchResults(searchResults, userInput):
    """
    Parses the result of a company search and returns company details.

    This function handles the case where the search returns multiple companies 
    by returning separate tuples containing the titles, tickers, and ciks for each 
    company found. If only one company is found, it returns a tuple with the 
    title, ticker, and cik of that company. If a key is missing in a company 
    dictionary (due to the search type), the user input is used in place of the missing key.

    Parameters:
    -----------
    searchResults : list
        A list of dictionaries where each dictionary contains company information 
        (such as 'ticker', 'title', 'cik_str') for one or more companies returned 
        from the search.

    userInput : str
        The original user input used for searching, which is used to replace any 
        missing keys in the search result (e.g., if searching by ticker, and 
        the result lacks the ticker, the input is used as the ticker).

    Returns:
    --------
    tuple or tuple of tuples
        If exactly one company is found, returns a tuple with 'title', 'ticker', 
        and 'cik'. If multiple companies are found, returns three tuples:
        - One with all the titles
        - One with all the tickers
        - One with all the ciks

    Example:
    --------
    searchResults = [
        {'ticker': 'NTWOU', 'title': 'Newbury Street II Acquisition Corp', 'cik_str': 2028027},
        {'ticker': 'XYZ', 'title': 'XYZ Corporation', 'cik_str': 2028030}
    ]
    
    userInput = 'NTWOU'

    result = parseSearchResults(searchResults, userInput)

    Output:
    -------
    Company 1:
    Ticker: NTWOU
    Title: Newbury Street II Acquisition Corp
    CIK: 2028027

    Company 2:
    Ticker: XYZ
    Title: XYZ Corporation
    CIK: 2028030

    Returns:
    -------
    (
        ('Newbury Street II Acquisition Corp', 'XYZ Corporation'),
        ('NTWOU', 'XYZ'),
        (2028027, 2028030)
    )
    """
    if not searchResults:
        print("No companies found.")
        return None

    # Prepare lists to store titles, tickers, and ciks
    titles = []
    tickers = []
    ciks = []

    # Iterate through each company in the search result
    for idx, company in enumerate(searchResults, start=1):
        # Handle missing keys depending on the result format
        title = company.get('title', 'N/A')
        ticker = company.get('ticker', 'N/A')
        cik = company.get('cik_str', 'N/A')

        # Replace missing keys with the user input
        if title == 'N/A':
            titles.append(userInput)
            tickers.append(ticker)
            ciks.append(str(cik))
        elif ticker == 'N/A':
            titles.append(title)
            tickers.append(userInput)
            ciks.append(str(cik))
        elif cik == 'N/A':
            titles.append(title)
            tickers.append(ticker)
            ciks.append(userInput)

    # If only one company is found, return a tuple (title, ticker, cik)
    if len(searchResults) == 1:
        return (titles[0], tickers[0], ciks[0])  # Return as a tuple even for one result

    # If multiple companies are found, return three tuples for titles, tickers, and ciks
    return tuple(titles), tuple(tickers), tuple(ciks)

###############################################
###############################################
# Search all companies functions
###############################################
###############################################

def browseAllCompanies(titleIndex, tickerIndex, cikIndex):
    """
    Displays all companies from the database in a paginated table format using the `tabulate` library.
    Allows the user to navigate through the list of companies and select one by entering the row number or performing pagination actions.

    Parameters:
    -----------
    titleIndex : dict
        A dictionary of company titles indexed by the title field, created by `createHashIndexes`.
    tickerIndex : dict
        A dictionary of companies indexed by ticker symbols, created by `createHashIndexes`.
    cikIndex : dict
        A dictionary of companies indexed by their Central Index Key (CIK), created by `createHashIndexes`.

    Returns:
    --------
    tuple or None
        A tuple containing the selected company's title, ticker, and CIK if a valid selection is made, 
        or None if the user does not make a valid selection.
    """
    # Prepare a list of all companies for tabulation, combining the title, ticker, and CIK for each company
    allCompanies = []

    for title, companies in titleIndex.items():
        for company in companies:
            ticker = company.get('ticker', 'N/A')
            cik = company.get('cik_str', 'N/A')
            allCompanies.append([title, ticker, cik])
    
    # Sort the companies alphabetically by their title
    companiesSorted = sortAllCompanies(allCompanies)

    # Get the height of the terminal to determine how many companies fit on one screen
    screenHeight = getTerminalHeight()
    
    currentPage = 0  # Start on the first page
    totalCompanies = len(companiesSorted)
    totalPages = (totalCompanies // screenHeight) + (1 if totalCompanies % screenHeight > 0 else 0)  # Calculate total pages

    while True:
        # Calculate the start and end indices for the current page of companies to display
        startIdx = currentPage * screenHeight
        endIdx = min(startIdx + screenHeight, totalCompanies)
        
        # Display the table of companies for the current page and get the user's action
        action = displayCompanyTable(companiesSorted, startIdx, endIdx, currentPage, totalPages)

        # Handle user input for navigation or selection
        if action == 'next' and currentPage < totalPages - 1:  # Move forward one page
            currentPage += 1

        elif action == 'back' and currentPage > 0:  # Move backward one page
            currentPage -= 1

        elif action.isdigit():  # User entered a row number
            selection = int(action)
            if 1 <= selection <= len(companiesSorted):  # Valid row selection
                # Return the selected company information (title, ticker, CIK)
                return companiesSorted[selection - 1][0], companiesSorted[selection - 1][1], companiesSorted[selection - 1][2]
            else:
                print("Invalid selection. Please enter a valid row number.")
                time.sleep(5)

        else:
            print("Invalid input. Please enter 'next', 'back', or a valid row number.")
        
        clearTerminal()

def displayCompanyTable(companiesSorted, startIdx, endIdx, currentPage, totalPages):
    """
    Displays a paginated table of companies in the terminal, including the row number, title, ticker, and CIK.
    Prompts the user to choose a company by entering a row number or selecting a navigation action.

    Parameters:
    -----------
    companiesSorted : list
        A list of companies sorted by their title. Each element is a list containing the title, ticker, and CIK.
    startIdx : int
        The starting index for the current page of companies to display.
    endIdx : int
        The ending index for the current page of companies to display.
    currentPage : int
        The current page number (zero-based).
    totalPages : int
        The total number of pages of companies.

    Returns:
    --------
    str
        A string representing the user's action (either a row number, 'next', 'back', or invalid input).
    """
    # Prepare a list of companies to display, including the row number as the first column
    companiesToDisplay = [[idx + 1] + company for idx, company in enumerate(companiesSorted[startIdx:endIdx], start=startIdx)]
    print(f"\nDisplaying page {currentPage + 1}/{totalPages} of companies.")
    
    # Display the table of companies
    print(tabulate(companiesToDisplay, headers=["Row", "Title", "Ticker", "CIK"], tablefmt="grid"))
        
    # Prompt the user for their action (select a company by row number, go to next/previous page, or jump to a letter)
    action = input("\nInput:\n\t-The row number of the company you want to select.\n\t-'Next' to go forward\n\t-'Back' to go back\n\tA letter (A-Z) to jump to a part of the alphabet.\nEnter: ").strip().lower()

    return action

def sortAllCompanies(allCompanies):
    """
    Sorts the allCompanies list alphabetically by their title.

    Parameters:
    -----------
    allCompanies : list of lists
        A list where each element is a list containing [title, ticker, cik] for a company.

    Returns:
    --------
    list of lists
        The sorted list of companies, with each element being a list [title, ticker, cik].
    """
    return sorted(allCompanies, key=lambda company: company[0].lower())  # Sort by the title (case-insensitive)