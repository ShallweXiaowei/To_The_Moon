# -*- coding: utf-8 -*-
"""
Created on Fri Apr 26 23:07:40 2024

@author: Xiaowei
"""

import pandas as pd
import json
import os
import utils

current_directory = os.getcwd()

with open(current_directory + "/submissions/CIK0000933141.json", 'r') as file:
    data = json.load(file)
    
cik = data["cik"]

own_insider = data["insiderTransactionForOwnerExists"]



dic = utils.get_cik_dic()

dic["CIK0000004127"]