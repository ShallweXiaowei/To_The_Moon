#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri Jan 10 17:29:40 2025

@author: xiaoweiyan
"""

import utils



index_list = ["SLG", "HITI","OPI","SPR","AAPL"]

p_df, ret_df, cor_df = utils.read_table_for_ticker(index_list)

ret_df.loc[:,"ave"] = ret_df.mean(axis = 1)
index_return = [1]

for i in range(ret_df.shape[0]):
    ret = ret_df["ave"].iloc[i]
    print(ret)