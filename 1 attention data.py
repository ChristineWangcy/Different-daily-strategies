import os
import pandas as pd
import bs4 as soup
import requests as request

link = 'https://www.yuncaijing.com/data/mai/p1.html'
page = request.get(link)
print(page.status_code)
exit()

def volmeasure(vol,compared_vol):
    if compared_vol == 0:
        return None
    if vol > 0 and compared_vol > 0:
        return vol/compared_vol

dir = '/Users/chunyanwang/Christine documents/projects/data files/daily data with indicators/stocks daily data - tushare/'
files = os.listdir(dir)
files.sort()

for f in files:
    print(f)
    if len(f) != 10:
        continue

    data = pd.read_csv(dir+f,header=0)
    num = len(data)
    print(num)
    if num > 10:
        # new indicators
        data['prevol'] = data['volume'].shift(1)
        data['pre9daysmaxvol'] = data['prevol'].rolling(9).max()
        data['vsprevol'] = data.apply(lambda x: volmeasure(x['volume'],x['prevol']),axis=1)
        data['vspre9daysmaxvol'] = data.apply(lambda x: volmeasure(x['volume'],x['pre9daysmaxvol']),axis=1)
        data = data.drop(columns=['prevol', 'pre9daysmaxvol'])
        data.to_csv(dir+f)

        print(f + ' is done.')
