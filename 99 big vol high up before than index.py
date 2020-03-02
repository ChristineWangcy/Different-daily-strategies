__author__ = 'clienttest'

'''
run download stock data everyday to download recent daily data from tushare to 
/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare downloaded
'''

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

def boolean_to_int(data):
    data = data.applymap(lambda x: 1 if x == True else x)
    data = data.applymap(lambda x: 0 if x == False else x)
    return data

def add_columns(data,stockname):
    # add stock name column
    dates = data.index.values
    num = len(data)
    to_buy = [0] * num
    buy = [0.00] * num
    to_sell = [0] * num
    sell = [0.00] * num
    overs = data['over tendays vol']
    tendays_vol = data['tendays vol']

    lows = data['low']
    pc = data['p_change']
    closes = data['close']
    opens = data['open']
    highs = data['high']
    close_index = data['close_index']
    high_index = data['high_index']
    data['index ma5'] = data['close'].rolling(5).mean()
    data = boolean_to_int(data)
    conti_up_3days = [0] * num


    #data['tendays same with index'] = data['same with index'].rolling(10).sum()
    #print('10% rank: ',top_tenth_rank,' 20% rank: ',top_twentyth_rank,' 50% rank: ',half_rank)
    for i in range(11,num):
        # first time over previous big vol high, recent not big profit, previous day not zhangting
        if overs[i] == True and overs[i-1] == False and \  
                                max(closes[i-5:i+1])/min(closes[i-5:i+1]) < 1.2 and highs[i-1] != closes[i-1]:
            to_buy[i] = 1
            for j in range(i-1,0,-1):
                if tendays_vol[j] != 9999:
                    big_vol_pos = j
                    # stock previous big vol lian zhang
                    if closes[j-1] < closes[j-2] or closes[j-2]<closes[j-3]:
                        to_buy[i] = 0
                        break

                    # dp not lian zhang
                    if close_index[j] > close_index[j-1] and ((close_index[j-1] > close_index[j-2] and \
                        close_index[j-2] > close_index[j-3]) or (high_index[j]>max(high_index[j-9:j]) and \
                        close_index[j] > close_index[j+1])):
                        to_buy[i] = 0
                        break

                    # stock over before dp over
                    for k in range(j+1,i+1):
                        if (close_index[k] > high_index[big_vol_pos] and closes[k] <= highs[big_vol_pos]) or \
                            (high_index[k] > high_index[big_vol_pos] and highs[k] <= highs[big_vol_pos]) or \
                                (low_index[k] >= low_index[big_vol_pos] and lows[k] <= lows[big_vol_pos]):
                            to_buy[i] = 0
                            break
                    break
            if to_buy[i] == 1:
                if i < num-1:
                    buy[i+1] = opens[i+1]
                    #print(f, dates[i+1], 'buy ', dates[i+1], buy[i+1])
    data['buy'] = buy

    # add indicator sell
    total_profits = [0] * num
    sell = [0] * num
    to_sell = [0] * num
    for i in range(10,num):
        if buy[i] > 0 and i < num-1:
            for j in range(i,num):
                if closes[j] < buy[i] * 1.05 or ((closes[j] > closes[j-1]*1.04 or closes[j] > buy[i]*1.05) and
                                                         close_index[j] < close_index[j-1]):
                    to_sell[j] = 1
                    if j < num-1:
                        sell[j+1] = opens[j+1]
                        total_profits[j+1] = sell[j+1]/buy[i] - 1
                        if total_profits[j+1] > 0.08 or total_profits[j+1] < -0.08:
                            print(f, dates[j+1], 'buy ',buy[i], 'sell ',sell[j+1])
                            print('total profit is: ', total_profits[j+1])
                    break

    data['sell'] = sell
    data['total profit'] = total_profits

    profits = [-9999] * num
    for i in range(0,num):
        if buy[i] > 0:
            profits[i] = closes[i]/buy[i] - 1
            if i+1 < num:
                for j in range(i,num):
                    if sell[j] > 0:
                        profits[j] = (sell[j] - closes[j-1])/closes[j-1]
                        for k in range(i,j):
                            if k != i:
                                profits[k] = pc[k] * 0.01
                        break

    data['profit'] = profits  # add more buy for stocks not sold yet, or else just keep for 1 day

    # change all true to 1, false to 0
    data = boolean_to_int(data)
    data = data[(data['profit'] != -9999)]
    data = data[['stock', 'buy','sell','profit','total profit','open','high','close','p_change','volume']]
    return data

all_data = pd.DataFrame()

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
files = os.listdir(dir)

for f in files:
    # 600177
    #if f == '002510.csv':
    #if f[3] != '3' and f[3] != '9':  # for data from dzh
    if f[0] != '9' and len(f) == 10: # for data from tushare
    #if f[3] == '0':
        # for data from dzh
        #data = pd.read_table(dir + f,
        #                     encoding='gb2312', header=None, names=['date', 'open', 'high', 'low', 'close', 'volume','turnover'])
        # for data from tushare
        data = pd.read_csv(dir + f, header=0)

        if 'industry profit rank' not in data.columns or 'industry profit rank in 6days' not in data.columns:
            continue
        #data = data.iloc[2:-1, :] #for data from dzh
        #data['stock'] = f[3:9]  # data from dzh
        data['stock'] = f[:6] # data from tushare

        # change date to standard date type from dzh
        #data = date_to_datetime(data)

        #if dp, choose date > 2010
        if f[0] == '9':
            data = data[pd.to_datetime(data['date']) > pd.to_datetime('20100101')]

        #set index
        data.set_index('date',inplace=True)
        data.sort_index(inplace=True)

        # change all str to float
        data['open'] = data['open'].astype('float')
        data['high_index'] = data['high_index'].astype('float')
        data['low']= data['low'].astype('float')
        data['close'] = data['close'].astype('float')
        data['volume'] =data['volume'].astype('float')


        # add more columns and indicators
        data = add_columns(data, f)

        # create new daily file with more columns
        #data.to_csv('/Users/chunyanwang/Christine documents/projects/data files/stocks daily data with indicators/' + f[3:9] +'_alldata.csv')


        # merge all_data with data1, create daily file merged by all files
        all_data = pd.concat([all_data,data])
        all_data.sort_index()
        #print(f+ ' done')
        print(len(data),len(all_data))
        all_data.to_csv('/Users/chunyanwang/Christine documents/projects/different daily strategies/99 big vol high up before than index all keeping data.csv')