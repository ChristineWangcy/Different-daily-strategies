import os
import pandas as pd
import datetime
import tushare as ts

stock_basic = pd.read_csv('/Users/chunyanwang/Christine documents/projects/data files/allstock data in one file/stocks basic info.csv', header=0)
stock_basic = stock_basic.groupby('industry')

dir = '/Users/chunyanwang/Christine documents/projects/data files/downloaded stock data/stocks daily data - tushare/'
dir_old = '/Users/chunyanwang/Christine documents/projects/data files/old downloaded stock data/'
current_dir = '/Users/chunyanwang/Documents/Christine/projects/different daily strategies/'
files = os.listdir(dir)

def remove_unnecessary_columns(data):
    cols = data.columns
    for c in cols:
        if 'Unnamed' in c or 'industry profit rank' in c or 'industry ave profit' in c:
            data = data.drop(c,axis=1)
    return data

all_industry_ave_profit = pd.DataFrame()

for s in stock_basic.groups:
    stocks = stock_basic.get_group(s)
    print('indus begin: ',stocks.iloc[0]['industry'])
    data = pd.DataFrame()
    for i in range(0, len(stocks)):
        stock_name_6byte = str(stocks.iloc[i]['code']).zfill(6)
        file = stock_name_6byte + '.csv'
        print('read stock: ',file)
        if file in files:
            stock_data = pd.read_csv(dir + file, encoding='latin-1')
            stock_data.to_csv(old_dir+file)
            if len(stock_data) > 20 and float(stock_data.iloc[0]['close']) > 0:
                data3 = pd.DataFrame()
                data3['date'] = stock_data['date']
                data3['stock'] = file[:6]
                data3['today profit'] = stock_data['close']/stock_data['close'].shift(1)-1
                data = pd.concat([data, data3])
                print(file + ' is read.')
    data = data.dropna()
    if len(data) > 10:
        data['industry profit rank'] = data.groupby('date')['today profit'].rank(ascending=False)
        data.loc[data['today profit'] == -9999,'today profit'] = None
        data_ave_profit = pd.DataFrame()
        data_ave_profit['industry ave profit'] = data.groupby(['date'])['today profit'].mean()
        all_industry_ave_profit[stocks.iloc[0]['industry']] = data_ave_profit['industry ave profit']
        
        data = data.merge(data_ave_profit,on='date',how='left')
        data = data.groupby(['stock'])
        for x in data.groups:
            data2 = data.get_group(x)
            data2 = data2.sort_values(['date'])
            file = str(data2.iloc[0]['stock']).zfill(6)+'.csv'
            if file in files:
                print(file + ' is going to be updated.' )
                stock1 = pd.read_csv(dir + file, header=0)
                stock1 = remove_unnecessary_columns(stock1)
                stock1.merge(data2[['date','industry profit rank','industry ave profit']],on='date',how='left').to_csv(dir+file)
                print(file + ' is updated.')
        
        print('indus is done: ', stocks.iloc[0]['industry'],'-----------')

all_industry_ave_profit_rank = all_industry_ave_profit.rank(axis=1,ascending=False)
all_industry_ave_profit_rank.to_csv(current_dir + 'all industry ave profit rank.csv')

all_industry_ave_profit_rank = pd.read_csv(dir_old + all industry ave profit rank.csv',header=0)

for f in files:
    data2 = pd.read_csv(dir + f, encoding="utf-8")
    #all_industry_ave_profit_rank = date_to_datetime(all_industry_ave_profit_rank)
    if 'industry' in data2.columns:
        industry_name = data2.iloc[0]['industry']
        print(industry_name)
        print(all_industry_ave_profit_rank.columns)
        if industry_name in all_industry_ave_profit_rank.columns:
            print(all_industry_ave_profit_rank.head(),data2.head())
            data4 = data2.merge(all_industry_ave_profit_rank[['date',industry_name]],on='date',how='left')
            print(data4.columns)
            data4.to_csv(dir+f,encoding='utf-8')
            print(f + ' is added with industry ave profit rank.')