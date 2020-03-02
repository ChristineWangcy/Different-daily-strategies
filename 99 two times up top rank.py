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
    buy = [0] * num
    overs = data['over tendays max']
    ranks = data['industry profit rank']
    ranks = ranks.replace(9999,0)
    max_rank = ranks.max()
    min_rank = ranks.min()
    top_ten_rank = int(min_rank+(max_rank-min_rank)/10)
    top_thirty_rank = int(min_rank+(max_rank-min_rank)/3)
    top_forty_rank = int(min_rank + (max_rank - min_rank) / 2.5)
    top_twentyth_rank = int(min_rank + (max_rank-min_rank)/5)
    half_rank = int(min_rank+(max_rank-min_rank)/2)
    lows = data['low']
    pc = data['p_change']
    closes = data['close']
    opens = data['open']
    highs = data['high']
    index_not_tp = data['index not tp']
    index_closes = data['close_index']
    index_profit = (index_closes-index_closes.shift(1))/index_closes.shift(1)
    data['index profit'] = index_profit
    data['same with index'] = (pc * index_profit > 0)
    data['index ma5'] = data['close'].rolling(5).mean()
    data = boolean_to_int(data)
    #data['tendays same with index'] = data['same with index'].rolling(10).sum()
    #print('10% rank: ',top_tenth_rank,' 20% rank: ',top_twentyth_rank,' 50% rank: ',half_rank)
    for i in range(11,num):
        if overs[i] == 1 and ranks[i] < top_forty_rank and (i==num-1 or (i < num-1 and lows[i+1] < closes[i]*1.02)) \
                and index_not_tp[i] == 1:
                #and index_closes[i] <= max(data['high_y'][i-5:i]) and opens[i+1] < closes[i] * 1.05:
            # and (data['ma5'][i-1]-data['ma5'][i-10]) * \
            #(data['index ma5'][i-1]-data['index ma5'][i-10]) > 0 \
            #    and max(closes[i-10:i])/min(closes[i-10:i]) < 1.12:
            to_buy[i] = 1
            # tp zhang top ranks
            up_start = 0
            for j in range(i,0,-1):
                if (lows[j] < lows[j-1] and closes[j] > opens[j] and closes[j-1]<=closes[j-2])\
                        or (lows[j-1] < lows[j-2] and closes[j-1]<opens[j-1] and closes[j-1] <closes[j-2] and
                                    closes[j] > opens[j]):
                    up_start = j
                    up_start_lowest = min(lows[j-1:i+1])
                    for k in range(j,i+1):
                        print(f,dates[k],ranks[k], half_rank)
                        if ranks[k] > half_rank or (k != i and ranks[k] < top_ten_rank):  #before tp not top to attract attention
                            to_buy[i] = 0
                            #print('not buy ',k,ranks[k],' top half rank ',half_rank)
                            break
                    break
            if to_buy[i] == 1 and up_start > 2:
                # previous high zhang top ranks
                for h in range(up_start-1,0,-1):
                    if highs[h] == data['tendays max'][i] and max(highs[h-4:h]) != data['tendays max'][i]:
                        if up_start_lowest != min(lows[h:up_start]):
                            #print('not buy ',f,lowest != min(lows[h:up_start]), max(closes[h-5:h+1]) != max(closes[h-1:up_start]))
                            to_buy[i] = 0
                            break
                        for j in range(h,0,-1):
                            if closes[j] > opens[j] and (lows[j] < lows[j-1] and closes[j-1]<closes[j-2] and closes[j-1] < opens[j-1])\
                            or (lows[j-1] < lows[j-2] and closes[j-1]<opens[j-1] and closes[j-1] <closes[j-2]):
                                print(f, 'previous up starts ', dates[j] , dates[h] , ranks[j:h + 1].mean(),
                                      ranks[j:h + 1].median(), top_forty_rank)
                                # previous up at least more than 3 days preparation but not top to attract others
                                prev_up_start = j
                                if  h-j < 2 or up_start_lowest < min(lows[prev_up_start:h]) or ranks[j:h+1].mean() > top_forty_rank or ranks[j:h+1].median() > top_forty_rank or \
                                    ranks[j:h+1].mean() < top_ten_rank:
                                    to_buy[i] = 0
                                    break
                                break
                        break
            if buy[i] == 1:
                print(f, 'buy ', dates[i+1], 'over tendays max ', data['tendays max'][i])
    data['buy'] = buy

    # add indicator sell
    total_profits = [0] * num
    sell = [0] * num
    to_sell = [0] * num
    for i in range(10,num):
        if data['buy'][i] > 0 and i < num-1:
            for j in range(i+1,num):
                if closes[j] < closes[j-1] and (closes[j] < opens[j] or index_closes[j]>index_closes[j-1]) :
                    if j == num - 1:
                        to_sell[j] = 1
                        break
                    if closes[j] < opens[i + 1] * 0.95 or lows[j] < lows[i]:
                        if j == num - 1:
                            to_sell[j] = 1
                            break
                        sell[j+1] = opens[j+1]
                        total_profits[j + 1] = sell[j + 1] / opens[i + 1] - 1
                        print(f, 'loss sell ', dates[j + 1], 'profit is ', total_profits[j + 1])
                        break
                    prev_high = max(highs[i:j+1])
                    for k in range(j+1,num):
                        if highs[k] >= prev_high:
                            if k == num-1:
                                to_sell[k] = 1
                                break
                            sell[k+1] = opens[k+1]
                            total_profits[k + 1] = sell[k + 1] / opens[i + 1] - 1
                            print(f, 'sell ', dates[k + 1], 'profit is ', total_profits[k + 1])
                            break
                        if closes[k] < opens[i + 1] * 0.95 or lows[k] < lows[i]:
                            if k == num - 1:
                                to_sell[k] = 1
                                break
                            sell[k+1] = opens[k+1]
                            total_profits[k + 1] = sell[k + 1] / opens[i + 1] - 1
                            print(f, 'loss sell ', dates[k + 1], 'profit is ', total_profits[k + 1])
                            break
                    break


    data['sell'] = sell
    data['to_sell'] = to_sell
    data['total profit'] = total_profits

    profits = [-9999] * num
    for i in range(0,num):
        if buy[i] == 1:
            profits[i] = 0
            if i+1 < num:
                profits[i+1] = (closes[i+1]-opens[i+1])/opens[i+1]
            if i+2 < num:
                for j in range(i+2,num):
                    if sell[j] > 0:
                        profits[j] = (sell[j] - closes[j-1])/closes[j-1]
                        for k in range(i+2,j):
                            profits[k] = pc[k] * 0.01
                        break

    data['profit'] = profits  # add more buy for stocks not sold yet, or else just keep for 1 day

    # change all true to 1, false to 0
    data = boolean_to_int(data)

    data = data[(data['profit'] != -9999)]
    data = data[['stock','industry profit rank','buy','sell','profit','total profit','same with index','open','high','close','p_change','tendays max','volume']]

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
        #print(len(data),len(all_data))
        all_data.to_csv('/Users/chunyanwang/Christine documents/projects/different daily strategies/99top rank all keeping data.csv')