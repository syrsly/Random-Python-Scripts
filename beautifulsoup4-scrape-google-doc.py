# This script was created as an answer to an employment quiz.
# The goal was to scrape a Google Doc's markup to parse a table into a secret message.
# I used PyScripter to format and test run this script.
# Some errors along the way. There's a lot of room for improvement. I kind of rushed this.
# The 're' package may be unnecessary. I imported it and added the normalize_key function because a stray character was throwing everything off, but the soup strip method probably could have handled this on its own.

# commands to install required libraries:
# pip install -U requests
# pip install -U beautifulsoup4

import requests
from bs4 import BeautifulSoup
import re

def normalize_key(key):
    """Normalize column headers by stripping and replacing any unicode dashes."""
    return re.sub(r'[\u2010\u2011\u2012\u2013\u2014\u2015\-]', '-', key.strip().lower())

def decode_and_print(url: str):
    url_response = requests.get(url)

    url_response.raise_for_status()
    # The raise_for_status() method checks the HTTP response code. If the response code indicates an error (like 4xx or 5xx), it raises an HTTPError; it otherwise does nothing for successful responses and continues the following code.

    soup = BeautifulSoup(url_response.text, 'html.parser')

    # Find the first table
    table = soup.find('table')
    if table is None:
        raise RuntimeError("Table not found in document")

    # Extract header names and rows
    header_row = table.find('tr')
    if header_row is None:
        raise RuntimeError("Table has no row data")

    header_cells = [normalize_key(td.get_text().strip()) for td in header_row.find_all('td')]

    rows = []
    for tr in table.find_all('tr'):
        cells = [td.get_text().strip() for td in tr.find_all('td')]
        if len(cells) != len(header_cells):
            continue
        rows.append(dict(zip(header_cells, cells)))

    # Parse into numeric coordinates and characters
    points = []
    for row in rows:
        print(row)
        try:
            x = int(row.get('x‑coordinate', row.get('x-coordinate')))
            y = int(row.get('y‑coordinate', row.get('y-coordinate')))
            ch = row.get('Character') or row.get('character') or ''
        except Exception as e:
            print(e)
            continue
        if len(ch) != 1:
            ch = ch if ch else ' '
        points.append((x, y, ch))

    if not points:
        print("(no points found)")
        return

    max_x = max(p[0] for p in points)
    max_y = max(p[1] for p in points)

    # Initialize grid with spaces
    grid = [ [' '] * (max_x + 1) for _ in range(max_y + 1) ]

    # Place characters
    for x, y, ch in points:
        grid[y][x] = ch

    # Print from top (max_y) down to 0 so that y=0 is bottom
    for y in range(max_y, -1, -1):
        line = ''.join(grid[y])
        print(line)

