# download recent 3 years stock data from tushare

import tushare as ts
import pandas as pd

symbols = pd.read_csv('/Users/chunyanwang/Documents/Christine/projects/data files/allstock data in one file/stocks symbol.csv')

pro = ts.pro_api('3c499aa556bbb3bba9be8ea9cb2e853cde79960872488b69db1df0a6')

def download_stock_hist():
    for s in symbols['symbols']:
        # download recent 3 years data
        #if not (str(s)[0] != '6' or s > 603255):
        #    continue
        ss = str(s).zfill(6)
        print(s,ss)
        '''
        if ss[0] == '6':
            code = ss+'.SH'
        if ss[0] == '0' or ss[0] == '3':
            code = ss+'.SZ'
        '''
        # df = ts.get_hist_data(str(ss),start='2019-09-01')
        df = ts.get_hist_data(str(ss)) # not qian fu quan
        #ts.set_token('3c499aa556bbb3bba9be8ea9cb2e853cde79960872488b69db1df0a6')
        #df = ts.pro_bar(ts_code=code, adj='qfq') # qian fu quan
        if isinstance(df, pd.DataFrame) and len(df) > 1:
            df.to_csv('/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/'+ ss +'.csv',encoding='utf_8_sig')
            print(ss + ' is downloaded')
download_stock_hist()

df = ts.get_hist_data('sh000001')
df.to_csv('/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/sh000001.csv',
    encoding='utf_8_sig')
print('sh000001 is downloaded')
