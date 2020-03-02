import os
import pandas as pd

def tendays_maxmin(maxmin,self_maxmin):
    if maxmin == self_maxmin:
        return self_maxmin

dir = '/Users/chunyanwang/Documents/Christine/projects/data files/downloaded stock data/stocks daily data - tushare/'
old_dir = '/Users/chunyanwang/Documents/Christine/projects/data files/old downloaded stock data/'
files = os.listdir(dir)

for f in files:

    data = pd.read_csv(dir+f,header=0)
    data.to_csv(old_dir+f)
    num = len(data)

    if num > 20 and len(f) == 10:
        data = data.set_index('date')
        data = data.sort_index()
        dates = list(data.index.values)
        highs = data['high']
        lows = data['low']
        closes = data['close']
        vols = data['volume']

        # new indicators
        data['tendays highest'] = highs.shift(-5).rolling(15).max()
        data['tendays lowest'] = lows.shift(-5).rolling(15).min()
        data['tendays maxvol'] = vols.rolling(10).max()

        data['tendays max'] = data.apply(lambda x: tendays_maxmin(x['tendays highest'],x['high']),axis=1)
        data['tendays min'] = data.apply(lambda x: tendays_maxmin(x['tendays lowest'],x['low']), axis=1)
        data['tendays vol'] = data.apply(lambda x: tendays_maxmin(x['tendays maxvol'],x['volume']),axis=1)
        data.to_csv(dir+f)

        print(f + ' is done.')

