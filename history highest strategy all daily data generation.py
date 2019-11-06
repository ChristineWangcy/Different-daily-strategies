__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']
    dateformat = '%Y/%m/%d'
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

def boolean_to_int(data):
    data = data.applymap(lambda x: 1 if x == True else x)
    data = data.applymap(lambda x: 0 if x == False else x)
    return data

def add_columns(data,stockname):
    # add stock name column
    data['stock'] = stockname

    # remove first row and change str to float
    data = data.iloc[1:, :]
    data['close'] = data['close'].astype(float)
    data['open'] = data['open'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)

    # add daily profit column
    closes = data['close'][1:]
    previous_closes = closes.shift(1)[1:]

    # this last day profit is actually next day profit
    data['last day profit'] = (closes[1:] - previous_closes[1:]) / previous_closes[1:]

    # next day profit
    data['next day profit'] = data['last day profit'].shift(-1)

    # add next day price
    data['next day open'] = data['open'].shift(-1)
    data['next day high'] = data['high'].shift(-1)
    data['next day low'] = data['low'].shift(-1)


    # add indicator recent 9 days highest, lowest, max volume
    data['prev 9 days high'] = data['high'].shift(1).rolling(9).max()
    #data['prev 9 days low'] = data['low'].shift(1).rolling(9).min()
    data['prev 9 days max vol'] = data['volume'].shift(1).rolling(9).max()

    # add indicator whether close > prev 9 days highest, Yes - 1, No - 0
    data['above 10 days high'] =  (data['close'] > data['prev 9 days high'])

    # add indicator whether volume > prev 9 days max volume, Yes - 1, No - 0
    data['above 10 days max vol'] =  (data['volume'] > data['prev 9 days max vol'])

    # add indicator whether close < prev 9 days lowest
    #data['below 10 days low'] = (data['close'] < data['prev 9 days low'])

    # add ma200 line
    #data['ma200'] = data['close'].rolling(200).mean()
    # add indicator whether price above 200 ave line
    #data['above ma200'] = data['close'] > data['ma200']

    # change all true to 1, false to 0
    data = boolean_to_int(data)

    # add indicator whether first time being highest/lowest close in 10 days
    data['1st time being 10 days high'] = ((data['above 10 days high'] * data['above 10 days high'].rolling(5).sum()) == 1)
    #data['1st time being 10 days low'] = ((data['below 10 days low'] * data['below 10 days low'].rolling(5).sum()) == 1)


    # add indicator previous history maximum value and whether today is the highest price
    highests = [data['high'][0]]
    is_highest = [1]
    is_close_highest = [1]
    for i in range(1,len(data['high'])):
        high = data['high'][i]
        close = data['close'][i]
        if close > highests[-1]:
            is_close_highest.append(1)
        else:
            is_close_highest.append(0)
        if high > highests[-1]:
            highests.append(high)
            is_highest.append(1)
        else:
            highests.append((highests[-1]))
            is_highest.append(0)
    data['history highest'] = highests
    data['is highest'] = is_highest
    data['is close highest'] = is_close_highest
    

    data = boolean_to_int(data)

    # add indicator total increase or decrease = sum of 1*above 10 days high and -1*below 10 days high
    #data['total increase or decrease'] = (data['1st time being 10 days high'] * 1 + data['1st time being 10 days low'] * -1).cumsum()

    # add column 'whether trading'
    data['trading'] = np.where(data['volume'].isnull(), '0', '1')

    all_data = pd.read_csv(
        '/Users/clienttest/Documents/Christine/projects/history highest price strategy/all daily data.csv')

    data = data[data['is close highest'] == 1]
    print(len(data))
#    data = data[data['1st time being 10 days high'] == 1]
#    print(len(data))
#    data = data[data['above 10 days max vol'] == 1]
#    print(len(data))

# remove next day when stock can not be bought
#    data = data[data['next day high'] != data['next day low']]

    return data

#all_data = pd.DataFrame(columns=['date', 'open', 'high', 'low', 'close', 'volume', 'turnover','stock',
#                                 'last day profit','trading','trading days','next day profit'])
all_data = pd.read_csv('/Users/clienttest/Documents/Christine/projects/history highest price strategy/all daily data.csv',\
                       header=0,index_col=0)
del all_data['date']
all_data.rename(columns = {all_data.columns[0]:'date'},inplace=True)
all_data.set_index('date')

dir = '/Users/clienttest/Documents/Christine/projects/data files/downloaded stock data/1014 daily/'
files = os.listdir(dir)

for f in files:
    # 600177
    #if int(f[3:9]) > 600400:
    #if f[3] != '3' and f[3] != '9':
    if f[3] == '0':
        data = pd.read_table(dir + f,
                             encoding='gb2312', header=None, names=['date', 'open', 'high', 'low', 'close', 'volume','turnover'])
        data = data.iloc[2:-1, :]
        data['stock'] = f[3:9]

        # change date to standard date type
        data = date_to_datetime(data)

        #if dp, choose date > 2010
        if f[3] == '9':
            data = data[pd.to_datetime(data['date']) > pd.to_datetime('20100101')]

        #set index
        data.set_index('date',inplace=True)
        data.sort_index(inplace=True)

        # change all str to float
        data['open'] = data['open'].astype('float')
        data['high'] = data['high'].astype('float')
        data['low']= data['low'].astype('float')
        data['close'] = data['close'].astype('float')
        data['volume'] =data['volume'].astype('float')


        # add more columns and indicators
        data = add_columns(data, f)

        # create new daily file with more columns
        #data.to_csv('/Users/clienttest/Documents/Christine/projects/data files/stocks daily data with indicators/' + f[3:9] +'_alldata.csv')

        ''' 
        # investigate indicator and price
        plt.subplot(2,1,1)
        plt.plot(data['close'])
        plt.subplot(2,1,2)
        plt.plot(data['total increase or decrease'])
        plt.savefig('/Users/clienttest/Documents/Christine/projects/data files/images/' + f[3:9] + '.png')
        plt.close('all')
        '''

        # merge all_data with data1, create daily file merged by all files
        all_data = pd.concat([all_data,data])
        print(f+ ' done')
        print(len(data),len(all_data))
        all_data.to_csv('/Users/clienttest/Documents/Christine/projects/history highest price strategy/all daily data.csv')

print(all_data)








