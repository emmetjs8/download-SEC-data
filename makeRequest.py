"""
File: makeRequests.py
Author: Emmet Szewczyk
Email: emmetjs@gmail.com
Version: 1.0
Date: 2024-12-27

This script provides a client for interacting with the SEC's EDGAR API, including a rate-limiting mechanism
that ensures compliance with the API's usage policies. The client allows for fetching data about companies
using their Central Index Key (CIK).

Classes:
    RateLimiter: Handles global rate limiting for API requests.
    EdgarClient: Provides methods for fetching data from the EDGAR API.

Usage:
    - Initialize the EdgarClient once and call makeRequest from anywhere in the program.
    - The rate limiter will enforce API limits globally.
"""

import time
import requests
from threading import Lock
from terminalUtils import clearTerminal

class RateLimiter:
    """
    A class to handle rate limiting for API requests.
    """
    def __init__(self, maxCalls, period):
        """
        Initialize the rate limiter.

        :param max_calls: Maximum number of API calls allowed.
        :param period: Time period (in seconds) for the maximum calls.
        """
        self.maxCalls = maxCalls
        self.period = period
        self.calls = 0
        self.startTime = time.time()
        self.lock = Lock()

    def wait(self):
        """
        Wait until the next API call is allowed if the rate limit is exceeded.
        """
        with self.lock:
            while True:
                currentTime = time.time()
                elapsed = currentTime - self.startTime

                if elapsed > self.period:
                    self.calls = 0
                    self.startTime = currentTime

                if self.calls < self.maxCalls:
                    self.calls += 1
                    return

                time.sleep(0.1)  # Wait a short time before re-checking


class EdgarClient:
    """
    A Singleton client for interacting with the SEC's EDGAR API.
    """
    _instance = None
    _lock = Lock()

    def __new__(cls, rateLimiter=None):
        """
        Implement Singleton pattern to ensure a single instance.
        """
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(EdgarClient, cls).__new__(cls)
                cls._instance.rateLimiter = rateLimiter
        return cls._instance

    def get_data(self, url, headers):
        """
        Fetch data from the EDGAR API.

        :param url: Full URL for the EDGAR API.
        :param headers: Headers for the API request.
        :return: JSON data from the API.
        """
        if self.rateLimiter:
            self.rateLimiter.wait()

        response = requests.get(url, headers=headers)
        if response.status_code != 200:

            return None

        return response.json()


def makeRequest(baseUrl, cikNum=None):
    """
    Create a request to the EDGAR API using a formatted URL.

    :param base_url: The base URL for the EDGAR API.
    :param cik_num: Central Index Key (CIK) of the company (optional).
    """
    if cikNum:
        fullUrl = baseUrl.replace("##########", cikNum.zfill(10))
    else:
        fullUrl = baseUrl

    # Get the global EdgarClient instance
    client = EdgarClient(rateLimiter=RateLimiter(maxCalls=10, period=60))  # Only initialized once
    headers = {
        "User-Agent": "Personal application/1.0 (emmetjs@gmail.com)"
    }

    try:
        companyData = client.get_data(fullUrl, headers)
        clearTerminal()
        return companyData
    except Exception as e:
        print(f"Error fetching data for CIK {cikNum}: {e}")
        time.sleep(5)
        clearTerminal()
        return None



