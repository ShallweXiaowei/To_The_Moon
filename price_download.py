# -*- coding: utf-8 -*-
"""
Created on Sun May 26 17:24:07 2024

@author: Xiaowei
"""

import pandas as pd

import yfinance as yf
import utils
import sqlite3
import logging
from datetime import date
import sys
import time
import os

def download_price_to_temp():

    last_date = input("taget last date in the db, YYYY-MM-dd: ")
    logger = logging.getLogger(__name__)
    
    # msft = yf.Ticker("MSFT")
    
    # # get all stock info
    # msft.info
    
    # # get historical market data
    # hist = msft.history(period="max")
    
    # hist.loc[:,"ticker"] = "MSFT"
    # hist.loc[:,"Date"] = hist.index
    # hist = hist.rename(columns={'Stock Splits': 'Split'})
    
    cik_map = utils.read_table_all("CIK_map", "CIK_map")
    # existing = utils.select_distinct_ticker()
    # to_download = [x for x in cik_map["ticker"] if x not in existing]
    # print("%d existing"%len(existing))
    
    period = pd.read_csv("latest_date.csv",index_col = 1).to_dict()
    
    indistry_map_dic = {}
    all_ticker = pd.read_csv("ticker.txt",sep = "\t").iloc[:,0].to_list()
    
    #def download_and_write_price(ticker):
    print("start looping")
    for ticker in all_ticker:
        try:
            ticker = ticker.upper()
            meta = yf.Ticker(ticker)
            industry = meta.info["industry"]
            industry_Disp = meta.info["industryDisp"]
            industry_Key = meta.info["industryKey"]
            sector = meta.info["sector"]
            sectorKey = meta.info["sectorKey"]
            sectorDisp = meta.info["sectorDisp"]
            indistry_map_dic[ticker] = [industry, industry_Disp,industry_Key,sector,sectorKey,sectorDisp]
        except:
            logger.info("Industry not found for %s"%ticker)
        
        if ticker not in period["start_date"]:
            hist = meta.history(period="max")
            time.sleep(1)
        else:
            end = period["end_date"][ticker].split(" ")[0]
            if end == last_date:
                print("%s already up to date"%ticker)
                continue
            
            hist = meta.history(period="max", start = end)  
            time.sleep(1)
        if hist.empty:
            #print("%s is empty"%ticker)
            continue
        hist.loc[:,"ticker"] = ticker
        hist.loc[:,"Date"] = hist.index
        hist = hist.rename(columns={'Stock Splits': 'Split'})
        try:
            #utils.write_df_to_db(hist, "price.db","stock_price")
            hist.to_csv("temp_price/{}_{}.csv".format(ticker,last_date))
    
        except:
            logger.info("%s price table cannot write")
        logger.info("finished download and write %s"%ticker)
    
    
    industry_df = pd.DataFrame(indistry_map_dic).transpose()
    industry_df.columns = ["industry","industry_Disp","indistry_map_dic", "sector", "sectorKey", "sectorDisp"]
    industry_df.to_csv("industry_map.csv")
    
    conn = sqlite3.connect('industry_map.db')  # Replace 'stock_data.db' with your database file
    
    industry_df.to_sql('industry_map.db', conn, if_exists='replace')
    print("write to industry_map.db")
    
def generate_latest_date_from_csv():
    print("start generating last date csv")
    utils.write_latest_day_csv()
    print("finished writing last date csv")
    
    
def write_temp_to_db():
    df_to_write = pd.DataFrame()
    i = 0
    for file in os.listdir('temp_price'):
        i+=1
        df = pd.read_csv("temp_price/%s"%file)
        df_to_write = pd.concat([df_to_write,df])
        if i%500 == 0:
            print ("finished %d"%i)
            
            
    df_to_write = df_to_write[['ticker', 'Open', 'High', 'Low', 'Close', 'Volume', 'Date','Dividends', 'Split']]
    
    df_to_write = df_to_write.dropna(subset=['ticker','Date'])
    df_to_write = df_to_write.drop_duplicates(subset=['ticker', 'Date'])
    
    utils.write_df_to_db_make_sure_unique(df_to_write, "price.db","stock_price",if_exists = "append")
    
        
    
    
    
    
    
    
if __name__ == "__main__":
    generate_latest_date_from_csv()
    download_price_to_temp()
    write_temp_to_db()