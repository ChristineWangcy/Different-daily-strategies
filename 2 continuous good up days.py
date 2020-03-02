import os
import pandas as pd
import datetime

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']
    dateformat = '%Y-%m-%d'  # data from dzh
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

def today_up_good(profit,close,open):
    if profit > 0 and close > 0 and open > 0:
        if close > open:
            return 1
        else:
            return 0
    else:
        return 0

def continuous_good_up_days(good, prev_good, prev2nd_good):
    result = 0
    if good ==  1:
        result = 1
        if prev_good == 1:
            result = 2
            if prev2nd_good == 1:
                result = 3
    return result


dir = '/Users/chunyanwang/Christine documents/projects/data files/daily data with indicators/stocks daily data - tushare/'
files = os.listdir(dir)

for f in files:
    data = pd.read_csv(dir+f,header=0,index_col=0)
    #print(data.head())
    #data = date_to_datetime(data)
    dates = list(data.index.values)
    if int(f[:6]) <= 2943:
        continue
    num = len(data)
    if num > 200 and data.iloc[1,6] > 0:
        # new indicators
        #data['today up good'] = data.apply(lambda x: today_up_good(x['today profit'],x['close'],x['open']),axis=1)
        #data['prev up good'] = data['today up good'].shift(1)
        #data['prev2nd up good'] = data['prev up good'].shift(1)
        #data['continuous good up days']  = data.apply(lambda x: continuous_good_up_days(x['today up good'],
        #                                                        x['prev up good'], x['prev2nd up good']),axis=1)
        data['today up good'] = data['today up good'].fillna(0)
        cons = [0] * num
        for i in range(200,num):
            for j in range(i,0,-1):
                if data['today up good'][j] != 1:
                    break
                else:
                    cons[i] += 1
        data['continuous good up days'] = cons
        data['up in 10 days'] = data['today up good'].rolling(10).sum()
        data.to_csv(dir+f)

        print(f + ' is done.')
    else:
        os.remove(dir+f)
        print(f + ' is removed.')