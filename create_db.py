# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 22:16:00 2024

@author: Xiaowei
"""

import sqlite3
import pandas as pd
import json
from pprint import pprint


# Connect to SQLite database
conn = sqlite3.connect('price.db')


#Create a cursor object to execute SQL commands
cursor = conn.cursor()

create_query = '''
CREATE TABLE stock_price (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    Open REAL, 
    High REAL,
    Low REAL,
    Close REAL,
    Volume INTEGER,
    Date TIMESTAMP,
    Dividends REAL,
    Split DECIMAL(2),
    UNIQUE (ticker, Date)
);
'''

cursor.execute(create_query)
conn.commit()
