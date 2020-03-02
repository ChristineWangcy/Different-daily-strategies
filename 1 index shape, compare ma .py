import os
import pandas as pd

read_dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
to_dir = '/Users/chunyanwang/Christine documents/projects/data files/daily data with indicators/stocks daily data - tushare/'
files = os.listdir(read_dir)

# read dp
index = pd.read_csv(read_dir+'sh000001.csv',header=0)
index['prev p_change'] = index['p_change'].shift(1)
index_prev_close = index['close'].shift(1)

# index profit and shape
index['open percent'] = index['open']/index_prev_close
index['prev open percent'] = index['open percent'].shift(1)
index_range = (index['high']-index['low'])+000000000000000000000.1
index['close_open percent'] = (index['close']-index['open'])/index_range
index['high_close percent'] = (index['high']-index['close'])/index_range
index['close_low percent'] = (index['close']-index['low'])/index_range
index['prev close_open percent'] = index['close_open percent'].shift(1)
index['prev high_close percent'] = index['high_close percent'].shift(1)
index['prev close_low percent'] = index['close_low percent'].shift(1)

# comparing with ave
index['ma60'] = index['close'].rolling(60).mean()
index['ma100'] = index['close'].rolling(100).mean()
index['ma200'] = index['close'].rolling(200).mean()
index['above ma5'] = index['close'] > index['ma5']
index['above ma10'] = index['close'] > index['ma10']
index['above ma20'] = index['close'] > index['ma20']
index['above ma60'] = index['close'] > index['ma60']
index['above ma100'] = index['close'] > index['ma100']
index['above ma200'] = index['close'] > index['ma200']

index['ma5 up'] = index['ma5'] > index['ma5'].shift(1)
index['ma10 up'] = index['ma5'] > index['ma10'].shift(1)
index['ma20 up'] = index['ma5'] > index['ma20'].shift(1)
index['ma60 up'] = index['ma5'] > index['ma60'].shift(1)
index['ma100 up'] = index['ma5'] > index['ma100'].shift(1)
index['ma200 up'] = index['ma5'] > index['ma200'].shift(1)

# updage index file
index.to_csv(to_dir+'sh000001.csv')

files.sort()
for f in files:
    if len(f) != 10:
        continue
    # add index indicators to data file
    data = pd.read_csv(read_dir+f,header=0)
    # add index basic info and shape
    data['index open'] = index['open']
    data['index high'] = index['high']
    data['index low'] = index['low']
    data['index vol'] = index['volume']
    data['index p_change'] = index['p_change']
    data['index prev p_change'] = index['prev p_change']
    data['index prev open percent'] = index['prev open percent']
    data['index close_open percent'] = index['close_open percent']
    data['index high_close percent'] = index['high_close percent']
    data['index close_low percent'] = index['close_low percent']
    data['index prev close_open percent'] = index['prev close_open percent']
    data['index prev high_close percent'] = index['prev high_close percent']
    data['index prev close_low percent'] = index['prev close_low percent']

    # add index moving average info
    data['index above ma5'] = index['above ma5']
    data['index above ma10'] = index['above ma10']
    data['index above ma20'] = index['above ma20']
    data['index above ma60'] = index['above ma60']
    data['index above ma100'] = index['above ma100']
    data['index above ma200'] = index['above ma200']
    data['index ma5 up'] = index['ma5 up']
    data['index ma10 up'] = index['ma10 up']
    data['index ma20 up'] = index['ma20 up']
    data['index ma60 up'] = index['ma60 up']
    data['index ma100 up'] = index['ma100 up']
    data['index ma200 up'] = index['ma200 up']
    
    data.to_csv(to_dir+f)
    print(f + ' is done.')