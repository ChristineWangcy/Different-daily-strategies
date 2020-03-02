import os
import pandas as pd

dir = '/Users/chunyanwang/Christine documents/projects/data files/daily data with indicators/stocks daily data - tushare/'
files = os.listdir(dir)
files.sort()

for f in files:
    if len(f) != 10:
        continue
    # read data
    data = pd.read_csv(dir+f,header=0)

    # stock shape
    data['prev p_change'] = data['p_change'].shift(1)
    data_prev_close = data['close'].shift(1)
    data['open percent'] = data['open']/data_prev_close
    data['prev open percent'] = data['open percent'].shift(1)
    data_range = (data['high']-data['low'])+000000000000000000000.1
    data['close_open percent'] = (data['close']-data['open'])/data_range
    data['high_close percent'] = (data['high']-data['close'])/data_range
    data['close_low percent'] = (data['close']-data['low'])/data_range
    data['prev close_open percent'] = data['close_open percent'].shift(1)
    data['prev high_close percent'] = data['high_close percent'].shift(1)
    data['prev close_low percent'] = data['close_low percent'].shift(1)

    # compare with ma
    data['ma60'] = data['close'].rolling(60).mean()
    data['ma100'] = data['close'].rolling(100).mean()
    data['ma200'] = data['close'].rolling(200).mean()
    data['above ma5'] = data['close'] > data['ma5']
    data['above ma10'] = data['close'] > data['ma10']
    data['above ma20'] = data['close'] > data['ma20']
    data['above ma60'] = data['close'] > data['ma60']
    data['above ma100'] = data['close'] > data['ma100']
    data['above ma200'] = data['close'] > data['ma200']

    data['ma5 up'] = data['ma5'] > data['ma5'].shift(1)
    data['ma10 up'] = data['ma5'] > data['ma10'].shift(1)
    data['ma20 up'] = data['ma5'] > data['ma20'].shift(1)
    data['ma60 up'] = data['ma5'] > data['ma60'].shift(1)
    data['ma100 up'] = data['ma5'] > data['ma100'].shift(1)
    data['ma200 up'] = data['ma5'] > data['ma200'].shift(1)

    data.to_csv(dir+f)
    print(f + ' is done.')
