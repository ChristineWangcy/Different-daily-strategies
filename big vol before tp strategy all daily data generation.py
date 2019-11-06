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

    num = len(data)
    # remove first row and change str to float
    #data = data.iloc[1:, :]
    data['close'] = data['close'].astype(float)
    data['open'] = data['open'].astype(float)
    data['high'] = data['high'].astype(float)
    data['low'] = data['low'].astype(float)

    # add daily profit column
    closes = data['close']
    previous_closes = closes.shift(1)
    # this last day profit is actually next day profit
    data['today profit'] = (closes - previous_closes) / previous_closes
    # next day profit
    data['next day profit'] = data['today profit'].shift(-1)
    # add next day price
    data['next day open'] = data['open'].shift(-1)
    data['next day high'] = data['high'].shift(-1)
    data['next day low'] = data['low'].shift(-1)


    # add indicator whether short peiod maximum price
    highs = data['high']
    maxhigh = [0] * num
    maxhigh_indexs = []
    for i in range(6,num-6):
        if highs[i] == max(highs[i-5:i+5]):
            maxhigh[i] = 1
            maxhigh_indexs.append(i)
    data['maxhigh'] = maxhigh

    # add indicator whether close over max high
    overs = [0] * num
    over_maxhigh = [0] * num
    for i in range(0,len(maxhigh_indexs)-1):
        start_maxhigh = maxhigh_indexs[i]
        end_maxhigh = maxhigh_indexs[i+1]
        for j in range(start_maxhigh+1,end_maxhigh):
            if closes[j] > highs[start_maxhigh]:
                if data['today profit'][j] < 0.97:
                    overs[j] = 1
                    over_maxhigh[i] = highs[start_maxhigh]
                break
    data['over'] = overs
    data['over maxhigh'] = over_maxhigh

    # add indicator whether there is bigger vol before over day vol
    vols = data['volume']
    opens = data['open']
    bigvol_before = [0] * num
    buy = [0] * num
    for i in range(0,num-1):
        if overs[i] == 1:
            bigvol = vols[i]
            for j in range(i-1,i-5,-1):
                if data['today profit'][j] > 0:
                    if vols[j] > bigvol:
                        bigvol = vols[j]
                else:
                    break
            if bigvol > vols[i]:
                bigvol_before[i] = 1
                buy[i] = opens[i+1]
    data['bigvol before'] = bigvol_before
    data['buy'] = buy

    # add indicator sell
    sell = [0] * num
    for i in range(5,num-1):
        if data['buy'][i] > 0:
            for j in range(i+1,num-1):
                if (vols[j] > data['bigvol before'][j] or closes[j] < data['over maxhigh'][j]) and data['next day profit'][j] > -0.96:
                    sell[j+1] = opens[j+1]
                    break
    data['sell'] = sell

    # change all true to 1, false to 0
    data = boolean_to_int(data)

    data = data[(data['buy'] > 0) | (data['sell'] > 0)]

    return data

all_data = pd.DataFrame()
#all_data = pd.read_csv('/Users/clienttest/Documents/Christine/projects/big vol before tp strategy/all daily data.csv',\
#                       header=0,index_col=0)
#del all_data['date']
#all_data.rename(columns = {all_data.columns[0]:'date'},inplace=True)
#all_data.set_index('date')

dir = '/Users/clienttest/Documents/Christine/projects/data files/downloaded stock data/1014 daily/'
files = os.listdir(dir)

for f in files:
    # 600177
    #if int(f[3:9]) == 600400:
    if f[3] != '3' and f[3] != '9':
    #if f[3] == '0':
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


        # merge all_data with data1, create daily file merged by all files
        all_data = pd.concat([all_data,data])
        print(f+ ' done')
        print(len(data),len(all_data))
        all_data.to_csv('/Users/clienttest/Documents/Christine/projects/big vol before tp strategy/all daily data.csv')








