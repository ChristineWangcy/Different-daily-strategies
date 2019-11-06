__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']
    dateformat = '%Y-%m-%d'
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

def add_columns(data,stockname):
    # add stock name column
    data['stock'] = stockname

    # add daily profit column
    data = data.iloc[1:, :]
    data['close'] = data['close'].astype(float)
    closes = data['close'][1:]
    previous_closes = closes.shift(1)[1:]
    data['last day profit'] = (closes[1:] - previous_closes[1:]) / previous_closes[1:]

    # add indicator whether first above 10 days max volume, Yes - 1, No - 0
    
    # add indicator whether first above 10 days highest 

    # add indicator whether dp above 10 days highest
    
    #update previous daily file with all new columns and indicators
    
    
    # resample by month  
    data1 = data.resample('M').last()

    # add column 'whether trading'
    data1['trading'] = np.where(data1['volume'].isnull(), '0', '1')
    #add column 'trading days in month' 
    data1['trading days'] = data.resample('W').count()['close']
    
    # add column 'next month profit'
    closes = data1['close'][:-1]
    next_month_closes = data1['close'].shift(-1)[:-1]
    data1 = data1.iloc[:-1, :]
    data1['next month profit'] = (next_month_closes - closes) / closes
    
    return data1

all_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'turnover','stock',
                                 'last day profit','trading','trading days','next month profit'])
all_data.set_index('date')

dir = '/Users/clienttest/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare downloaded/'
files = os.listdir(dir)
for f in files:
    if f[0] != '3':
        data = pd.read_csv(dir + f)
        print(data.head())

        # change date to standard date type
        data = date_to_datetime(data)

        #set index
        data.set_index('date',inplace=True)

        # add more columns and indicators
        data1 = add_columns(data, f)

        # create new monthly file with more columns
        data1.to_csv('data files/stocks monthly data with indicators/' + f +'_alldata.csv')

        #merge all_data with data1, create monthly file merged by all files
        all_data = pd.concat([all_data,data1])
        print(f+ ' done')
        print(len(data1),len(all_data))
        all_data.to_csv('data files/allstock data in one file/monthly all data.csv')
print(all_data)