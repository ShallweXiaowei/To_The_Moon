# -*- coding: utf-8 -*-
"""
Created on Sat Apr 27 00:25:15 2024

@author: Xiaowei
"""


import pandas as pd
import json
from pprint import pprint
import requests
import sqlite3
from sqlalchemy import create_engine, MetaData, Table, select, distinct, text
from sqlalchemy.orm import sessionmaker
import time
import seaborn as sns
import matplotlib.pyplot as plt

def get_cik_dic():
    cik_dic = pd.read_csv("ticker.txt",delimiter = "\t",header = None,index_col = 0)
    cik_dic = cik_dic[cik_dic.index.notna()]
    cik_dic = cik_dic.loc[~cik_dic.index.str.contains("-")]
    cik_dic = cik_dic.to_dict()[1]
    
    cik_dic = {"CIK"+"0"*(10-len(str(v)))+str(v):str(k).upper() for k,v in cik_dic.items()}
    
    return cik_dic


def fill_cik(cik):
    return "CIK"+"0"*(10-len(str(cik)))+str(cik)


########## write dataframe to SQL
def write_df_to_db(df, db, table_name, index = False, if_exists = "append"):
    conn = sqlite3.connect(db)
    df.to_sql(table_name,conn, index = index,if_exists = if_exists)
    conn.close()
    #print("table %s has been written successfully"%table_name)
    return

def write_df_to_db_make_sure_unique(df, db, table_name, index = False, if_exists = "append"):
    conn = sqlite3.connect(db)
    cursor = conn.cursor()
    for _, row in df.iterrows():
        cursor.execute('''
            INSERT OR IGNORE INTO stock_price (ticker, Open, High, Low, Close, Volume, Date, Dividends,
                  Split)
            VALUES (?, ?, ?,?,?,?,?,?,?)
        ''', (row['ticker'], row['Open'], row['High'], row['Low'], row['Close'], row['Volume'], row['Date'], row['Dividends'], row['Split']))
        
    conn.commit()
    conn.close()
    return
        
        
#########read the entile table
def read_table_all(database, table_name):
    engine = create_engine('sqlite:///%s.db'%database)
    df = pd.read_sql_table(table_name, engine)
    return df


def select_distinct_ticker():
    engine = create_engine('sqlite:///price.db')
    metadata = MetaData()
    metadata.reflect(bind=engine)
    stock_prices = metadata.tables['stock_price']
    Session = sessionmaker(bind=engine)
    session = Session()
    query = select(distinct(stock_prices.c.ticker))
    unique_tickers = session.execute(query).scalars().all()
    session.close()
    return unique_tickers

def ticker_start_end_date():
    conn = sqlite3.connect('price.db')
    query = """
    SELECT 
        ticker,
        MIN(date) AS start_date,
        MAX(date) AS end_date
    FROM 
        stock_price
    GROUP BY 
        ticker;
    """
    s = time.time()
    df = pd.read_sql_query(query, conn)
    print("query start and end date used %f seconds"%(time.time() - s))
    # Close the database connection
    conn.close()
    return df

def write_latest_day_csv():
    df = ticker_start_end_date()
    df.to_csv("latest_date.csv")
    print("latest date csv generated")


# Define the SQL query

def read_table_for_ticker(ticker_list):
    ticker_list = tuple(ticker_list)
    #ticker_list = ("AAPL","MSFT","TSLA","NVDA", "SLG","REI","BA","SPR", "HITI")
    if len(ticker_list)>1:
        sql_query = "SELECT Date, Close, ticker FROM stock_price WHERE ticker IN %s AND Date > '2022-01-01'"%str(ticker_list)
    else:
        sql_query = "SELECT Date, Close, ticker FROM stock_price WHERE ticker = '%s' AND Date > '2022-01-01'"%str(ticker_list[0])
    # Read the data into a Pandas DataFrame
    s = time.time()
    conn = sqlite3.connect('price.db')
    df = pd.read_sql_query(sql_query, conn)
    conn.close()
    print("query used %f seconds"%(time.time() - s))
    pf = df.pivot_table(index='Date', columns='ticker', values='Close')
    pf.index = pd.to_datetime(pf.index,utc=True)
    ret = pf.pct_change(1,fill_method=None).dropna()
    corr = ret.corr()
    
    # plt.figure(figsize=(25, 15))
    # sns.heatmap(corr, annot=True, cmap='coolwarm', fmt=".2f",annot_kws={"size": 16})
    # plt.title('Correlation Matrix Heatmap')
    # plt.show()
    return pf, ret, corr



def calculate_d1_reletive_ret(df):
    return df/df.iloc[0] - 1

### the first is the table, the second is the dic
def get_industry_dic():
    ind_map = pd.read_csv("industry_map.csv", index_col = 0)
    
    sector_ind_map = {}
    
    for i,row in ind_map.iterrows():
        sector = row["sector"]
        industry = row["industry"]
        if sector not in sector_ind_map:
            sector_ind_map[sector] = {industry:[i]}
        else:
            if industry not in sector_ind_map[sector]:
                sector_ind_map[sector][industry] = [i]
            else:
                sector_ind_map[sector][industry].append(i)
                
    return ind_map, sector_ind_map


if __name__ == "__main__":
    #write_latest_day_csv()
    print(read_table_for_ticker(["NVDA","MSFT"]))

    