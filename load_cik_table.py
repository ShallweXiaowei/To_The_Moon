# -*- coding: utf-8 -*-
"""
Created on Sun Apr 28 12:51:48 2024

@author: Xiaowei
"""

import utils
import os
import json
import pandas as pd


current_directory = os.getcwd()

dic = utils.get_cik_dic()
table_dic = {"entity":[],"CIK":[],"Full_CIK":[],"ticker":[]}

i = 0
for file in os.listdir(current_directory+"/companyfacts"):
    try:
        with open(current_directory + "/companyfacts/%s"%file, 'r',encoding='utf-8') as f:
            data = json.load(f)
        entity = data["entityName"]
        cik = data["cik"]
    except:
        continue
    full_cik = utils.fill_cik(cik)
    if full_cik not in dic:
        print ("%s not in list"%full_cik)
    else:
        ticker = dic[full_cik]
        
        table_dic["entity"].append(entity)
        table_dic["CIK"].append(cik)
        table_dic["Full_CIK"].append(full_cik)
        table_dic["ticker"].append(ticker)
    
    i+=1
    if i%500 == 0:
        print ("processing json file %d"%i)
    
df = pd.DataFrame(table_dic)

df.to_csv("CIK_map.csv")


df = pd.read_csv("CIK_map.csv")


utils.write_df_to_db(df, "CIK_map.db", "CIK_map")

