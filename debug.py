#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sat Mar  1 19:49:31 2025

@author: xiaoweiyan
"""


import utils



ticker_list=["NVDA"]
pf, ret, corr = utils.read_table_for_ticker(ticker_list)