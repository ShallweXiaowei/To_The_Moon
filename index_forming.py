import utils
import pandas as pd


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
