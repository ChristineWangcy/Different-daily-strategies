import os
import pandas as pd
import numpy as np

def over(prev_high,tendaysmax,closes,prev5days_high):
    if prev_high < tendaysmax and closes > max(tendaysmax,prev5days_high):
        return 1

def below(prev_low,tendaysmin,closes,prev5days_low):
    if prev_low > tendaysmin and closes < min(tendaysmin,prev5days_low):
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
old_dir = '/Users/chunyanwang/Documents/Christine/projects/data files/old downloaded stock data/'

files = os.listdir(dir)
for f in files:
    #if int(f[:6]) > 2473:
    #    break
    data = pd.read_csv(dir+f,header=0)
    data.to_csv(old_dir+f)
    num = len(data)
    if  num > 20 and data.iloc[1,3] > 0 and len(f) == 10:
        data = data.set_index('date')
        data = data.sort_index()
        dates = list(data.index.values)
        # if data file is empty
        vols = data['volume']
        #profits = data['today profit']
        highs = data['high']
        lows = data['low']
        closes = data['close']
        #ave200 = data['ave200']

        # add columns prev 5 days high/low, prev closes
        data['prev5days high'] = highs.shift(1).rolling(5).max()
        data['prev5days low'] = lows.shift(1).rolling(5).min()
        data['prev close'] = closes.shift(1)
        data['prev high'] = highs.shift(1)
        data['prev low'] = lows.shift(1)

        prev_closes = data['prev close']

        # fill in tendays max/min space with previous max/min
        data['tendays max'] = data['tendays max'].replace('',np.nan).ffill()
        data['tendays min'] = data['tendays min'].replace('',np.nan).ffill()

        maxvol_high = [0.00] * num
        for i in range(0,num):
            if data['tendays vol'][i] != 9999:
                maxvol_high[i] = highs[i]
        data['tendays maxvol high'] = maxvol_high
        data['tendays maxvol high'] = data['tendays maxvol high'].replace(0.00,np.nan).ffill()
        print(f, data['tendays maxvol high'])


        # whether today close is higher than previous period max high, or today close is lower than previous min low
        data = data.replace('',9999)
        data = data.replace(np.nan,9999)
        data['over tendays max']= data.apply(lambda x: over(x['prev high'], x['tendays max'], x['close'], \
                                   x['prev5days high']), axis=1)
        data['below tendays min'] = data.apply(lambda x: below(x['prev low'], x['tendays min'],x['close'],\
                                                                                 x['prev5days low']), axis=1)
        data['over tendays vol'] = closes > data['tendays maxvol high']

        #trending:over high and above ave 200 - up; below min and below ave 200 - down;
        # over high and below ave 200 - fan tan; below min and above 200 - tiaozheng;
        # else, over ave 200, up pai huai; below ave 200, down pai huai.
        #data['trend'] = data.apply(lambda x: trend(x['close'], x['ave200'], x['tendays max'], x['tendays min']),\
        #                                  axis=1)

        data.to_csv(dir+f)

        print(f + ' is done.')