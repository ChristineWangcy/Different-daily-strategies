import os
import pandas as pd
import datetime
import tushare as ts

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']

    #dateformat = '%Y/%m/%d' # data from dzh
    dateformat = '%Y-%m-%d'
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

#stocks_basic = ts.get_stock_basics()
#stocks_basic.to_csv('/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks basic info.csv',encoding='utf-8')
stock_basic = pd.read_csv('/Users/chunyanwang/Documents/Christine/projects/data files/allstock data in one file/stocks basic info.csv', header=0)
stock_basic = stock_basic.set_index(['code'])
stock_basic = stock_basic.sort_index()

dir = '/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/'
dir_old = '/Users/chunyanwang/Documents/Christine/projects/data files/old downloaded stock data/'

files = os.listdir(dir)

for f in files:
    data = pd.read_csv(dir+f,header=0,encoding='latin-1')
    data.to_csv(dir_old+f)
    if f[0] == '.':
        continue
    #if int(f[:6]) == 6:
    #    break

    num = len(data)
    if num > 20 and data.iloc[1,6] > 0 and len(f) == 10: # stock data file not empty
        # change date to standard date type
        data = date_to_datetime(data)

        # if dp, choose date > 2010
        if f[0] == '9':
            data = data[pd.to_datetime(data['date']) > pd.to_datetime('20100101')]

        # set index
        data.set_index('date', inplace=True)
        data.sort_index(inplace=True)

        # new indicators
        f1 = int(f[:6])
        if f1 in stock_basic.index:
            info = stock_basic.loc[f1]
            data['industry'] = info['industry']
            data.to_csv(dir+f)
            print(f + ' is done.')