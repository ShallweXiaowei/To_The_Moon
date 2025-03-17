import utils
import pandas as pd
import matplotlib.pyplot as plt



def get_d0_return(tickers,start_date=None, end_date=None,mean = True):
    pf,ret,corr = utils.read_table_for_ticker(tickers,start_date,end_date)
    d0_ret = utils.calculate_d1_reletive_ret(pf)
    
    thresdhold = d0_ret.std().mean() + 3*d0_ret.std().std()
    for i in d0_ret.std().index:
        if d0_ret.std()[i] > thresdhold:
            print ("%s is greater than threshold"%i)
            d0_ret = d0_ret.drop(columns = [i])
            
    
    if mean:
        mean = d0_ret.mean(axis = 1)
        return mean
    else:
        return d0_ret


if __name__ == "__main__":
    
    ind_map, sector_map = utils.get_industry_dic()



    ind = "Financial Services"
    sector_mean = {}
    
    for sector in sector_map[ind].keys():
        
        l = sector_map[ind][sector]
        
        
        
        pf,ret,corr = utils.read_table_for_ticker(l)
        
        
        d0_ret = utils.calculate_d1_reletive_ret(pf)
        
        mean = d0_ret.mean(axis = 1)
        sector_mean[sector+"_"+str(d0_ret.shape[1])] = mean
        
        
    df = pd.DataFrame(sector_mean)
    thresdhold = df.std().mean() + 2*df.std().std()
    for i in df.std().index:
        if df.std()[i] > thresdhold:
            print ("%s is greater than threshold"%i)
            df = df.drop(columns = [i])
    
    df.plot(figsize = (15,7.5))
    plt.show()