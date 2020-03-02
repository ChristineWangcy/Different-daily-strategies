# download recent 3 years stock data from tushare

import tushare as ts
import pandas as pd

symbols = pd.read_csv('/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks symbol.csv')

def download_stock_hist():
    for s in symbols['symbols']:
        #download recent 3 years data
        if len(str(s)) < 6:
            print(str(s))
            ss = '0' * (6-len(str(s))) + str(s)
            print(ss)
        else:
            ss = str(s)
        df = ts.get_hist_data(str(ss),start='2019-09-01')
        if isinstance(df, pd.DataFrame) and len(df) > 1:
            df.to_csv('/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'+ ss +'.csv',encoding='utf_8_sig')
            print(ss + ' is downloaded')

download_stock_hist()

import os
import pandas as pd
import datetime
import tushare as ts

# change column date to standard date form
def date_to_datetime(datain):
    old_date = datain['date']

    #dateformat = '%Y/%m/%d' # data from dzh
    dateformat = '%Y-%m-%d'
    new_date = []
    for d in old_date:
        date1 = datetime.datetime.strptime(d, dateformat)
        new_date.append(date1)
    datain['date'] = new_date
    return datain

#stocks_basic = ts.get_stock_basics()
#stocks_basic.to_csv('/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks basic info.csv',encoding='utf-8')
stock_basic = pd.read_csv('/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks basic info.csv', header=0)
stock_basic = stock_basic.set_index(['code'])
stock_basic = stock_basic.sort_index()

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
files = os.listdir(dir)

for f in files:
    data = pd.read_csv(dir+f,header=0,encoding='latin-1')
    if f[0] == '.':
        continue
    #if int(f[:6]) == 6:
    #    break

    num = len(data)
    if num > 20 and data.iloc[1,6] > 0: # stock data file not empty
        # change date to standard date type
        data = date_to_datetime(data)

        # if dp, choose date > 2010
        if f[0] == '9':
            data = data[pd.to_datetime(data['date']) > pd.to_datetime('20100101')]

        # set index
        data.set_index('date', inplace=True)
        data.sort_index(inplace=True)

        # new indicators
        f1 = int(f[:6])
        if f1 in stock_basic.index:
            info = stock_basic.loc[f1]
            data['industry'] = info['industry']
            data.to_csv(dir+f)
            print(f + ' is done.')
    else:
        os.remove(dir+f)
        print(f + ' is removed.')

import os
import pandas as pd
import datetime
import tushare as ts

stock_basic = pd.read_csv(
    '/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks basic info.csv',
    header=0)
stock_basic = stock_basic.groupby('industry')

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'

files = os.listdir(dir)


def remove_unnecessary_columns(data):
    cols = data.columns
    for c in cols:
        if 'industry profit rank' in c or 'industry ave profit' in c:
            data = data.drop(c, axis=1)
    return data


all_industry_ave_profit = pd.DataFrame()

for s in stock_basic.groups:
    stocks = stock_basic.get_group(s)
    print('indus begin: ', stocks.iloc[0]['industry'])
    data = pd.DataFrame()
    for i in range(0, len(stocks)):
        stock_name_6byte = str(stocks.iloc[i]['code']).zfill(6)
        file = stock_name_6byte + '.csv'
        print('read stock: ', file)
        if file in files:
            stock_data = pd.read_csv(dir + file, encoding='latin-1')
            if len(stock_data) > 20 and float(stock_data.iloc[0]['close']) > 0:
                data3 = pd.DataFrame()
                data3['date'] = stock_data['date']
                data3['stock'] = file[:6]
                data3['today profit'] = stock_data['close'] / stock_data['close'].shift(1) - 1
                data = pd.concat([data, data3])
                print(file + ' is read.')
    data = data.dropna()
    if len(data) > 10:
        data['industry profit rank'] = data.groupby('date')['today profit'].rank(ascending=False)
        data.loc[data['today profit'] == -9999, 'today profit'] = None
        data_ave_profit = pd.DataFrame()
        data_ave_profit['industry ave profit'] = data.groupby(['date'])['today profit'].mean()
        all_industry_ave_profit[stocks.iloc[0]['industry']] = data_ave_profit['industry ave profit']

        data = data.merge(data_ave_profit, on='date', how='left')
        data = data.groupby(['stock'])
        for x in data.groups:
            data2 = data.get_group(x)
            data2 = data2.sort_values(['date'])
            file = str(data2.iloc[0]['stock']).zfill(6) + '.csv'
            if file in files:
                print(file + ' is going to be updated.')
                stock1 = pd.read_csv(dir + file, header=0)
                stock1 = remove_unnecessary_columns(stock1)
                stock1.merge(data2[['date', 'industry profit rank', 'industry ave profit']], on='date',
                             how='left').to_csv(dir + file)
                print(file + ' is updated.')

        print('indus is done: ', stocks.iloc[0]['industry'], '-----------')

all_industry_ave_profit_rank = all_industry_ave_profit.rank(axis=1, ascending=False)
all_industry_ave_profit_rank.to_csv('/Users/chunyanwang/Christine documents/projects/'
                                    'different daily strategies/all industry ave profit rank.csv')

all_industry_ave_profit_rank = pd.read_csv('/Users/chunyanwang/Christine documents/projects/'
                                           'different daily strategies/all industry ave profit rank.csv',
                                           header=0)

for f in files:
    data2 = pd.read_csv(dir + f, encoding="utf-8")
    # all_industry_ave_profit_rank = date_to_datetime(all_industry_ave_profit_rank)
    if 'industry' in data2.columns:
        industry_name = data2.iloc[0]['industry']
        print(industry_name)
        print(all_industry_ave_profit_rank.columns)
        if industry_name in all_industry_ave_profit_rank.columns:
            print(all_industry_ave_profit_rank.head(), data2.head())
            data4 = data2.merge(all_industry_ave_profit_rank[['date', industry_name]], on='date', how='left')
            print(data4.columns)
            data4.to_csv(dir + f, encoding='utf-8')
            print(f + ' is added with industry ave profit rank.')
            
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


import os
import pandas as pd

def tendays_maxmin(maxmin,self_maxmin):
    if maxmin == self_maxmin:
        return self_maxmin

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
files = os.listdir(dir)

for f in files:
    if len(f) !=10:
        continue
    data = pd.read_csv(dir+f,header=0)
    data = data.set_index('date')
    data = data.sort_index()

    dates = list(data.index.values)

    num = len(data)

    if num > 20:
        highs = data['high']
        lows = data['low']
        closes = data['close']

        # new indicators
        data['tendays highest'] = highs.shift(-3).rolling(9).max()
        data['tendays lowest'] = lows.shift(-3).rolling(9).min()
        data['tendays max close'] = closes.shift(-3).rolling(9).max()
        data['tendays min close'] = closes.shift(-3).rolling(9).min()

        data['tendays max'] = data.apply(lambda x: tendays_maxmin(x['tendays highest'],x['high']),axis=1)
        data['tendays min'] = data.apply(lambda x: tendays_maxmin(x['tendays lowest'],x['low']), axis=1)

        data.to_csv(dir+f)

        print(f + ' is done.')


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

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
files = os.listdir(dir)
for f in files:
    #if int(f[:6]) > 2473:
    #    break
    data = pd.read_csv(dir+f,header=0)
    data = data.set_index('date')
    data = data.sort_index()
    dates = list(data.index.values)

    num = len(data)
    if num > 20 and data.iloc[1,3] > 0:
        if len(f) != 10:
            continue
        # if data file is empty
        vols = data['volume']
        #profits = data['today profit']
        highs = data['high']
        lows = data['low']
        closes = data['close']
        #ave200 = data['ave200']

        # add columns prev 5 days high/low, prev closes
        data['prev5days high'] = highs.shift(1).rolling(3).max()
        data['prev5days low'] = lows.shift(1).rolling(3).min()
        data['prev close'] = closes.shift(1)
        data['prev high'] = highs.shift(1)
        data['prev low'] = lows.shift(1)

        prev_closes = data['prev close']

        # fill in tendays max/min space with previous max/min
        data['tendays max'] = data['tendays max'].replace('',np.nan).ffill()
        data['tendays min'] = data['tendays min'].replace('',np.nan).ffill()

        # whether today close is higher than previous period max high, or today close is lower than previous min low
        data = data.replace('',9999)
        data = data.replace(np.nan,9999)
        data['over tendays max']= data.apply(lambda x: over(x['prev high'], x['tendays max'], x['close'], \
                                   x['prev5days high']), axis=1)
        data['below tendays min'] = data.apply(lambda x: below(x['prev low'], x['tendays min'],x['close'],\
                                                                                 x['prev5days low']), axis=1)

        #trending:over high and above ave 200 - up; below min and below ave 200 - down;
        # over high and below ave 200 - fan tan; below min and above 200 - tiaozheng;
        # else, over ave 200, up pai huai; below ave 200, down pai huai.
        #data['trend'] = data.apply(lambda x: trend(x['close'], x['ave200'], x['tendays max'], x['tendays min']),\
        #                                  axis=1)

        data.to_csv(dir+f)

        print(f + ' is done.')
        
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

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
files = os.listdir(dir)

index_data_shh = pd.read_csv('/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare downloaded/000000sh.csv',header=0)
index_data_shz = pd.read_csv('/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare downloaded/000000sz.csv',header=0)

for f in files:
    #if int(f[:6]) > 2473:
    #    break
    data = pd.read_csv(dir+f,header=0)
    data = data.set_index('date')
    data = data.sort_index()
    dates = list(data.index.values)

    num = len(data)
    index_not_tp = [0] * num
    if num > 20 and data.iloc[1,3] > 0:
        if len(f) > 10:
            continue
        if f[0] == '0':
            data = data.merge(index_data_shh[['date','high','close']],on='date',how='left')
        if f[0] == '6' or f[0] == '3':
            data = data.merge(index_data_shh[['date','high','close']],on='date',how='left')
        data = data.rename(columns={'close_x':'close','high_x':'high','close_y':'close_index','high_y':'high_index'})
        for i in range(10,num):
            if data['over tendays max'][i] == 1:
                for j in range(i-2,0,-1):
                    if data['high'][j] == data['tendays max'][i]:
                        if max(data['high_index'][j+1:i]) < data['high_index'][j]:
                            index_not_tp[i] = 1
                        break
        data['index not tp'] = index_not_tp
        data.to_csv(dir+f)

        print(f + ' is done.')

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
    buy = [0] * num
    overs = data['over tendays max']
    ranks = data['industry profit rank']
    ranks = ranks.replace(9999,0)
    max_rank = ranks.max()
    min_rank = ranks.min()
    top_thirty_rank = int(min_rank+(max_rank-min_rank)/3)
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
    data['index ma5'] = data['close_y'].rolling(5).mean()
    data = boolean_to_int(data)
    #data['tendays same with index'] = data['same with index'].rolling(10).sum()
    #print('10% rank: ',top_tenth_rank,' 20% rank: ',top_twentyth_rank,' 50% rank: ',half_rank)
    for i in range(11,num-1):

        if overs[i] == 1 and index_not_tp[i] == 1 and ranks[i] < top_twentyth_rank and lows[i+1] < closes[i]*1.02 and \
                        index_closes[i] <= max(data['high_index'][i-5:i]) and opens[i+1] < closes[i] * 1.05:
            #and (data['ma5'][i-1]-data['ma5'][i-10]) * \
            #(data['index ma5'][i-1]-data['index ma5'][i-10]) > 0 \
            #    and max(closes[i-10:i])/min(closes[i-10:i]) < 1.12:
            buy[i] = 1
            # tp zhang top ranks
            up_start = 0
            for j in range(i,0,-1):
                if (lows[j] < lows[j-1] and closes[j] > opens[j] and closes[j-1]<=closes[j-2])\
                        or (lows[j-1] < lows[j-2] and closes[j-1]<opens[j-1] and closes[j-1] <closes[j-2] and
                                    closes[j] > opens[j]):
                    up_start = j
                    lowest = min(lows[j-1:i+1])
                    for k in range(j,i+1):
                        print(f,dates[k],ranks[k], top_twentyth_rank)
                        if ranks[k] > top_twentyth_rank:
                            buy[i] = 0
                            print('not buy ',k,ranks[k],' top twentyth rank ',top_twentyth_rank)
                            break
                    break
            if buy[i] == 1 and up_start > 0:
                # previous high zhang top ranks
                for h in range(up_start-1,0,-1):
                    if highs[h] == data['tendays max'][i] and highs[h-1] != data['tendays max'][i]:
                        if lowest != min(lows[h:up_start]):
                            print('not buy ',f,lowest != min(lows[h:up_start]), max(closes[h-5:h+1]) != max(closes[h-1:up_start]))
                            buy[i] = 0
                            break
                        for j in range(h,0,-1):
                            if (lows[j] < lows[j-1] and closes[j] > opens[j] and closes[j-1]<closes[j-2] and closes[j-1] < opens[j-1])\
                            or (lows[j-1] < lows[j-2] and closes[j-1]<opens[j-1] and closes[j-1] <closes[j-2] and
                                        closes[j] > opens[j]):
                                if closes[h] > closes[h-1]:
                                    to_h = h+1
                                else:
                                    to_h = h
                                for k in range(j,to_h):
                                    if ranks[k] > top_thirty_rank:
                                        print('not buy ',f,dates[k],ranks[k]>top_thirty_rank)
                                        buy[i] = 0
                                        break
                                break
                        break
            if buy[i] == 1:
                print(f, 'buy ', dates[i+1], 'tendays max ', data['tendays max'][i])
    data['buy'] = buy

    # add indicator sell
    total_profits = [0] * num
    sell = [0] * num
    for i in range(10,num-1):
        if data['buy'][i] > 0:
            prev_max_close = max(closes[i-10:i])
            for j in range(i+1,num-1):
                if ((closes[j] > closes[j-1] * 1.05 or closes[j-1] > closes[j-2]*1.05) and ranks[j] < top_twentyth_rank and (index_closes[j] < index_closes[j-1] or
                                                          (index_closes[j-1] > index_closes[j-2] and
                                                                   closes[j-1] < closes[j-2]))
                    ) or closes[j] < prev_max_close or index_closes[j] < min(index_closes[j-10:j]):
                    print(ranks[j],top_twentyth_rank,index_closes[j],index_closes[j-1],closes[j],prev_max_close)
                    sell[j+1] = opens[j+1]
                    total_profits[j+1] = sell[j+1]/opens[i+1] - 1
                    print(f, 'sell ', dates[j+1], 'profit is ', total_profits[j+1])
                    break

                '''
                if ranks[j] > data['industry profit rank in 6days'][j] or ranks[j] > half_rank or \
                    closes[j] < opens[i+1] * 0.9 or lows[j] < lows[i]:
                    if opens[j+1] > opens[i+1] * 1.05:
                        sell[j+1] = opens[j+1]
                        print('big profit sell ',sell[j+1]/opens[i+1]-1)
                        total_profits[j+1] = sell[j+1]/opens[i+1]-1
                        if total_profits[j+1] > 0.1:
                            print('+++++++++++++++++++++++',data.iloc[j+1][['stock']],' ',opens[i+1],' ', sell[j+1])
                    else:
                        prev_high = max(highs[i:j+1])
                        for k in range(j+1,num):
                            if highs[k] >= prev_high:
                                sell[k] = prev_high
                                print('profit sell ',prev_high/opens[i+1]-1)
                                total_profits[k] = prev_high/opens[i+1]-1
                                break
                            if closes[k] > closes[k-1] and index_closes[k] > index_closes[k-1] and ranks[k] > half_rank:
                                sell[k+1] = opens[k+1]
                                print('ruo yu dp profit: ', sell[k+1]/opens[i+1] - 1)
                                break
                            if closes[k] < opens[i+1] * 0.95 or lows[k] < opens[i+1] * 0.9:
                                sell[k+1]  = opens[k+1]
                                print('lose sell ',sell[k+1]/opens[i+1] - 1)
                                total_profits[k+1] = sell[k+1]/opens[i+1] - 1
                                if total_profits[k+1] < -0.08:
                                    print('--------------------',data.iloc[k+1][['stock']],' ',opens[i+1],' ', sell[k+1])
                                break
                    break
                '''
    data['sell'] = sell
    data['total profit'] = total_profits

    profits = [0] * num
    for i in range(0,num):
        if buy[i] == 1:
            profits[i] = 0.0000000000001
            profits[i+1] = (closes[i+1]-opens[i+1])/opens[i+1]
            for j in range(i+1,num):
                if sell[j] > 0:
                    profits[j] = (sell[j] - closes[j-1])/closes[j-1]
                    if j > i+2:
                        for k in range(i+2,j):
                            profits[k] = pc[k] * 0.01
                    break

    data['profit'] = profits  # add more buy for stocks not sold yet, or else just keep for 1 day

    # change all true to 1, false to 0
    data = boolean_to_int(data)

    data = data[(data['profit'] != 0)]
    data = data[['stock','industry profit rank','buy','sell','profit','total profit','same with index','open','high','close','p_change','tendays max','volume']]

    return data

all_data = pd.DataFrame()
#all_data = pd.read_csv('/Users/chunyanwang/Christine documents/projects/big vol before tp strategy/all daily data.csv',\
#                       header=0,index_col=0)
#del all_data['date']
#all_data.rename(columns = {all_data.columns[0]:'date'},inplace=True)
#all_data.set_index('date')

#dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/1014 daily/'
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
        data['high'] = data['high'].astype('float')
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

    __author__ = 'clienttest'

    import pandas as pd
    import matplotlib.pyplot as plt
    import os
    import datetime
    import numpy as np

    data = pd.read_csv(
        '/Users/chunyanwang/Christine documents/projects/different daily strategies/99top rank all keeping data.csv')
    # del data['date']
    # data.rename(columns = {data.columns[0]:'date'},inplace=True)
    '''
    dates = []
    for d in data['date']:
        dates.append(d.strip(' 0:00'))
    '''
    # sort by date and stock symbol
    data.sort_values(by=['date', 'stock'], inplace=True)

    # every year
    year = '2019'
    data = data[pd.to_datetime(data['date']) >= pd.to_datetime(year + '0101')]
    data = data[pd.to_datetime(data['date']) < pd.to_datetime(str(int(year) + 1) + '0101')]

    print(data)

    output = pd.DataFrame()

    output['new buy stocks amount'] = data.groupby('date')['stock'].count()

    # add a column trading value = volume * price, select stock by top 5 minimum trading value
    data['trading value'] = data['volume'] * data['close']
    data['trading value rank'] = data.groupby('date')['trading value'].rank()
    data = data[data['trading value rank'] <= 10]

    # create another file including data with all indicators
    data.to_csv(
        '/Users/chunyanwang/Christine documents/projects/different daily strategies/999industry ave profit rank with new indicators.csv')

    # get mean profit of the selected stocks
    print(data['profit'])
    output['selected stocks average profit'] = data.groupby('date')['profit'].mean()
    output.replace(np.nan, 0, inplace=True)

    output.to_csv(
        '/Users/chunyanwang/Christine documents/projects/different daily strategies/999industry ave profit rank output profit.csv')

    # add list of selected stocks name and their mean profit into the output file; get the total cumprod profit of all stocks and selected stocks
    data['stock'] = data['stock'].astype(str)
    output['stocks names'] = data.groupby('date')['stock'].agg(lambda col: ' '.join(col))

    # output['line_allstock_totalprofit'] = (output['all stocks next day average profit'] + 1).cumprod()
    output['line_selectedstock_totalprofit'] = (output['selected stocks average profit'] + 1 - 0.003).cumprod()
    num = len(output)
    max_drawdown = [0] * num
    totalprofit = output['line_selectedstock_totalprofit']
    for i in range(1, num - 1):
        max_drawdown[i] = (min(totalprofit[i + 1:]) - totalprofit[i]) / totalprofit[i]
    output['max drawdown'] = max_drawdown

    output.to_csv(
        '/Users/chunyanwang/Christine documents/projects/different daily strategies/999industry ave profit rank output profit.csv')

    # print final total profit, compare all stock profit and selected stock profit:
    # print('final all stocks profit: ', output['line_allstock_totalprofit'][-1]*100,'%')
    print('final selected stocks profit: ', output['line_selectedstock_totalprofit'][-1] * 100, '%')
    print('max drowdown is: ', min(output['max drawdown']))

    # plot
    # plt.plot(output['line_allstock_totalprofit'])
    fig = plt.figure(figsize=(40.0, 15.0))
    fig1 = fig.add_subplot(211)
    fig1.plot(output['line_selectedstock_totalprofit'])
    fig1.set_title('profit in year ')
    '''
    fig2 = fig.add_subplot(312)
    fig2.plot(output['new buy stocks amount'])
    fig2.set_title('new buy stocks amount')
    '''
    fig3 = fig.add_subplot(212)
    fig3.plot(output['max drawdown'])
    fig3.set_title('max drawdown')
    # fig2.set_xticks(output['date'])
    plt.show()
    plt.savefig(
        '/Users/chunyanwang/Christine documents/projects/different daily strategies/999industry ave profit rank.csv' \
        + year + '.png')
    plt.close('all')
    # plt.legend(loc='best')
    
    