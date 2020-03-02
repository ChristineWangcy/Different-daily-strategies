import os
import pandas as pd
import numpy as np

def over(prev_close,tendaysmax,closes,prev5days_high):
    if prev_close < tendaysmax and closes > max(tendaysmax,prev5days_high):
        return 1

def below(prev_close,tendaysmin,closes,prev5days_low):
    if prev_close > tendaysmin and closes < min(tendaysmin,prev5days_low):
        return 1

def trend(closes,ave200,tendays_max,tendays_min):
    #print(closes, ave200, tendays_max, tendays_min)
    if closes == 'NaN' or ave200 == 'NaN' or tendays_max== 'NaN' or tendays_min == 'NaN':
        return None
    if closes > ave200:
        if closes > tendays_max:
            return 'up'
        else:
            if closes < tendays_min:
                return 'tz'
            else:
                return 'upph'
    if closes < ave200:
        if closes > tendays_max:
            return 'ft'
        else:
            if closes < tendays_min:
                return 'down'
            else:
                return 'downph'

dir = '/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/'
dir_old = '/Users/chunyanwang/Documents/Christine/projects/data files/old downloaded stock data/'
files = os.listdir(dir)

index_data_shh = pd.read_csv('/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/sh000001.csv',header=0)
index_data_shh = index_data_shh.rename(columns={index_data_shh.columns[0]:'date','high': 'high_index', 'close': 'close_index', 'volume': 'vol_index','low': 'low_index', 'open': 'open_index'})

index_data_shh = index_data_shh.set_index('date')
for f in files:
    #if int(f[:6]) > 2473:
    #    break
    data = pd.read_csv(dir+f,header=0)
    data.to_csv(dir_old+f)
    num = len(data)
    index_not_tp = [0] * num
    if num > 20 and data.iloc[1,3] > 0 and len(f) == 10:
        data = data.set_index('date')
        #dates = list(data.index.values)
        data = pd.merge(data,index_data_shh[['high_index','close_index','vol_index','low_index','open_index']],on='date',how='left')
        
        '''
        for i in range(10,num):
            if data['over tendays max'][i] == 1:
                for j in range(i-2,5,-1):
                    if data['high'][j] == data['tendays max'][i] and max(data['high'][j-4:j]) != data['tendays max'][i]:
                        if max(data['high_index'][j+1:i]) < data['high_index'][j]:
                            index_not_tp[i] = 1
                        break
        data['index not tp'] = index_not_tp
        '''
        data.to_csv(dir+f)

        print(f + ' is done.')