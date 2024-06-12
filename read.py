# -*- coding: utf-8 -*-
"""
Created on Mon Mar 11 19:09:10 2024

@author: Xiaowei
"""

import pandas as pd
import json
from pprint import pprint
import requests


with open("CIK0000320193.json", 'r') as file:
    data = json.load(file)


facts = data['facts']


def read_item(data, key):
    return pd.DataFrame(data["facts"]["us-gaap"][key]["units"]["USD"])



asset = read_item(data,"Assets")
asset.index = pd.to_datetime(asset["filed"])

asset["val"].plot()


def get_cik_dic():
    cik_dic = pd.read_csv("ticker.txt",delimiter = "\t",header = None,index_col = 0)
    cik_dic = cik_dic.to_dict()[1]
    cik_dic = {v:k for k,v in cik_dic.items()}
    
    return cik_dic


