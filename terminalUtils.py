"""
Terminal Utility Functions

This script contains utility functions for managing terminal interactions, 
such as clearing the screen and determining the terminal's height.

Functions in this file:
-----------------------
- clearTerminal(): Clears the terminal screen. Compatible with both Windows 
  and Unix-based systems (macOS/Linux).
- getTerminalHeight(): Returns the number of rows that fit on the terminal 
  screen, factoring in space for table headers and borders.

Dependencies:
-------------
- `os` - For interacting with the operating system and clearing the terminal.

Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
"""

import os

def clearTerminal():
    """
    Clears the terminal screen based on the operating system.
    Works on both Windows and Unix-based systems (macOS/Linux).
    """
    os.system('cls' if os.name == 'nt' else 'clear')

def getTerminalHeight():
    """
    Returns the number of rows (lines) that fit on the terminal screen.
    """
    try:
        return os.get_terminal_size().lines - 2  # Subtract 2 for table headers and borders
    except OSError:
        return 20  # Default to 20 if terminal size can't be detected