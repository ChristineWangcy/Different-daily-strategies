import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']

    dateformat = '%Y/%m/%d' # data from dzh
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

files = os.listdir(dir)
for f in files:
    if f[3] != '3': # SH999999.TXT is sh index which is to 11/19/2019
        data = pd.read_table(dir + f,
                  encoding='gb2312', header=None, names=['date', 'open', 'high', 'low', 'close', 'volume','turnover'])
        data = data.iloc[2:-1]
        symbol = f[3:9]
        data['stock'] = symbol
        print(symbol, data.head())

        # change date from / to -
        data = date_to_datetime(data)

        #set index
        data.set_index('date',inplace=True)
        data.sort_index(inplace=True)

        # change all str to float
        data['open'] = data['open'].astype('float')
        data['high'] = data['high'].astype('float')
        data['low']= data['low'].astype('float')
        data['close'] = data['close'].astype('float')
        data['volume'] =data['volume'].astype('float')

        # adding profits columns
        closes = data['close']
        previous_closes = closes.shift(1)
        data['today profit'] = (closes - previous_closes) / previous_closes
        data['next day profit'] = data['today profit'].shift(-1)

        # add next day price
        data['next day open'] = data['open'].shift(-1)
        data['next day high'] = data['high'].shift(-1)
        data['next day low'] = data['low'].shift(-1)
        data['next day close'] = data['close'].shift(-1)

        data.to_csv('/Users/chunyanwang/Christine documents/projects/data files/daily data with indicators/stocks daily data - tushare/'+symbol+'.csv')
