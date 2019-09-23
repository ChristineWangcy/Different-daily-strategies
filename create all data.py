__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

all_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'turnover','stock',
                                 'last day profit','trading','trading days','next week profit'])
all_data.set_index('date')

dir = '/Users/clienttest/Documents/Christine/projects/downloaded stock data/DAILY NEW HIGH/'
files = os.listdir(dir)
for f in files:
    if f[3] != '3':
    #if f[] == 'SH$601838.TXT':
        data = pd.read_table(dir + f,
                             encoding='gb2312',header=None,names=['date','open','high','low','close','volume','turnover'])
        print(data.head())
        data = data.iloc[2:-1,:]
        data['stock'] = f[3:9]

        #change date to standard date type and set date as index
        old_date = data['date']
        dateformat = '%Y/%m/%d'
        outdate = '%y-%m-%d'
        new_date = []
        for d in old_date:
            date1 = datetime.datetime.strptime(d,dateformat)
            new_date.append(date1)
        data['date'] = new_date
        data.set_index('date',inplace=True)

        # add daily profit column
        data = data.iloc[1:,:]

        data['close'] = data['close'].astype(float)
        closes = data['close'][1:]
        previous_closes = closes.shift(1)[1:]

        data['last day profit'] = (closes[1:] - previous_closes[1:])/previous_closes[1:]

        #resample by week, add columns 'whether trading', 'trading days in week' and 'next week profit'

        data1 = data.resample('W').last()
        data1['trading'] = np.where(data1['volume'].isnull(),'0','1')
        data1['trading days'] = data.resample('W').count()['close']

        closes = data1['close'][:-1]
        next_week_closes = data1['close'].shift(-1)[:-1]
        data1 = data1.iloc[:-1,:]
        data1['next week profit'] = (next_week_closes-closes)/closes

        data1.to_csv('stocks weekly data/' + f +'_alldata.csv')

        #merge all_data with data1
        all_data = pd.concat([all_data,data1])
        print(f+ ' done')
        print(len(data1),len(all_data))
        all_data.to_csv('weekly all data.csv')
print(all_data)