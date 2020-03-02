import os
import pandas as pd

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'

files = os.listdir(dir)

for f in files:
    data = pd.read_csv(dir+f,header=0)
    if 'date' not in data.columns:
        os.remove(dir+f)
        print(f + ' is removed.')
        continue
    data = data.set_index('date')
    data = data.sort_index()
    num = len(data)

    if num > 20 and 'industry profit rank' in data.columns:

        # new indicators
        data['industry profit rank in 2days'] = data['industry profit rank'].rolling(2).mean()
        data['industry profit rank in 3days'] = data['industry profit rank'].rolling(3).mean()
        data['industry profit rank in 4days'] = data['industry profit rank'].rolling(4).mean()
        data['industry profit rank in 5days'] = data['industry profit rank'].rolling(5).mean()
        data['industry profit rank in 6days'] = data['industry profit rank'].rolling(6).mean()

        data.to_csv(dir+f)

        print(f + ' is done.')
