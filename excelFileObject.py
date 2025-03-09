import xlwings as xw
import pandas as pd

class FinancialExcelFile:
    def __init__(self, fileName):
        """Initialize the Excel file object.
        
        Args:
            fileName (str): Name of the Excel file to create.
        """
        self.fileName = fileName
        self.app = xw.App(visible=False)
        self.book = self.app.books.add()

    def addSheetWithData(self, sheetName, dataframe):
        """Add a sheet with data from a DataFrame.

        Args:
            sheet_name (str): Name of the sheet.
            dataframe (pd.DataFrame): Data to add to the sheet.
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")

        # Create a new sheet or get an existing one
        if sheetName in [sheet.name for sheet in self.book.sheets]:
            sheet = self.book.sheets[sheetName]
        else:
            sheet = self.book.sheets.add(sheetName)

        # Write the column headers
        sheet.range('A1').value = dataframe.columns.tolist()

        # Write the DataFrame values (excluding the index) starting from next row
        sheet.range('A2').value = dataframe.values
    
    def addDataFromCell(self, sheetName, dataframe, startCell):
        """Add data to a sheet starting from a specific cell in a DataFrame.

        Args:
            sheetName (str): Name of the sheet.
            dataframe (pd.DataFrame): Data to add to the sheet.
            startCell (str): The starting cell in the sheet where data will be inserted (e.g., 'A1').
        """
        if not isinstance(dataframe, pd.DataFrame):
            raise ValueError("Data must be a pandas DataFrame")

        # Create a new sheet or get an existing one
        if sheetName in [sheet.name for sheet in self.book.sheets]:
            sheet = self.book.sheets[sheetName]
        else:
            sheet = self.book.sheets.add(sheetName)

        # Get the sheet object
        sheet = self.book.sheets[sheetName]

        # Write the column headers starting from the specified cell
        sheet.range(startCell).value = dataframe.columns.tolist()

        # Write the DataFrame values (excluding the index) starting from row 2
        sheet.range(updateCellString(startCell, 0, 1)).value = dataframe.values
    
    def addCellToSheet(self, sheetName, cellsToAdd, dataInCells):
        """
        Adds data to specific cells in a specified sheet.
        
        This method takes in a sheet name, a list of cells to add data to, and the corresponding 
        data for each cell. It writes the data to the specified cells.

        Args:
            sheetName (str): The name of the sheet where the data will be written.
            cellsToAdd (list): A list of cell addresses (e.g., ['A1', 'B2', 'C3']) where data will be inserted.
            dataInCells (list): A list of data values to be written to the corresponding cells in `cellsToAdd`.

        Raises:
            ValueError: If the length of `cellsToAdd` and `dataInCells` do not match.
            KeyError: If the specified `sheetName` does not exist in the workbook.
        """
        
        # Check if sheetName exists in the workbook
        if sheetName not in [sheet.name for sheet in self.book.sheets]:
            raise KeyError(f"Sheet '{sheetName}' does not exist in the workbook.")
        
        # Get the sheet object
        sheet = self.book.sheets[sheetName]
        
        # Check if cellsToAdd and dataInCells have the same length
        if len(cellsToAdd) != len(dataInCells):
            raise ValueError("The length of 'cellsToAdd' and 'dataInCells' must be the same.")
        
        # Iterate over the cells and data to add to the sheet
        for i in range(len(cellsToAdd)):
            # Write the data to the corresponding cell
            sheet.range(cellsToAdd[i]).value = dataInCells[i]

    def saveAndClose(self):
        """Save and close the Excel file."""
        self.app.visible = False  # Ensure Excel stays hidden
        self.book.save(self.fileName)
        self.book.close()
        self.app.quit() # CLose Excel

def column_index_to_letter(col_index):
    """Converts a column index to a column letter (e.g., 1 -> 'A', 28 -> 'AB').
    
    Args:
        col_index (int): The column index to convert (1 for 'A', 2 for 'B', etc.).
    
    Returns:
        str: The corresponding column letter(s).
    """
    col_letter = ''
    while col_index > 0:
        col_index, remainder = divmod(col_index - 1, 26)
        col_letter = chr(65 + remainder) + col_letter
    return col_letter

def updateCellString(originalCell, moveCellHorizontally, moveCellVertically):
    """Iterate a cell reference by a given number of steps horizontally and vertically using xlwings,
    with error handling for out-of-bounds cells.

    Args:
        originalCell (str): The original cell reference in Excel format (e.g., 'A1', 'B2').
        moveCellHorizontally (int): The number of steps to move horizontally. Positive moves to the right, negative to the left.
        moveCellVertically (int): The number of steps to move vertically. Positive moves down, negative moves up.

    Returns:
        str: The new cell reference after moving horizontally and vertically.

    Raises:
        ValueError: If the resulting cell is out of Excel's valid range.
    """
    # Split the cell string into column letter and row number
    col_letter = ''.join([char for char in originalCell if char.isalpha()])  # Extract column letters
    row = int(''.join([char for char in originalCell if char.isdigit()]))  # Extract row number

    # Convert the column letter to its corresponding index
    col_index = 0
    for char in col_letter:
        col_index = col_index * 26 + (ord(char.upper()) - ord('A') + 1)

    # Calculate the new column index and row number
    new_col_index = col_index + moveCellHorizontally
    new_row = row + moveCellVertically

    # Check if the new column index and row are within valid Excel ranges
    if new_col_index < 1 or new_col_index > 16384:  # Excel supports columns A-ZZZZ (1 to 16384)
        raise ValueError(f"Column index {new_col_index} is out of bounds. Valid column range is 1 to 16384.")
    
    if new_row < 1:  # Excel rows start at 1, so the minimum valid row is 1
        raise ValueError(f"Row number {new_row} is out of bounds. Valid row range is 1 to 1048576.")
    
    # Convert the new column index back to a column letter using the custom function
    new_col_letter = column_index_to_letter(new_col_index)

    # Return the new cell reference as a string
    return f'{new_col_letter}{new_row}'



