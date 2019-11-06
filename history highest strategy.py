__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np


dir = '/Users/clienttest/Documents/Christine/projects/'

data = pd.read_csv(dir+'history highest price strategy/all daily data.csv')

del data['date']
data.rename(columns = {data.columns[0]:'date'},inplace=True)

dates = []
for d in data['date']:
    dates.append(d.strip(' 0:00'))

data['date'] = dates

# sort by date and stock symbol
data.sort_values(by=['date','stock'],inplace=True)


year = '2015'
#delete trading time too early before 2006
data = data[pd.to_datetime(data['date']) >= pd.to_datetime(year + '0101')]
data = data[pd.to_datetime(data['date']) < pd.to_datetime(str(int(year)+1) + '0101')]

#delete stocks not traded in last day
data = data[data['trading'] != 0]

#delete stocks trading days < 10 in a month
#data = data[data['trading days'] > 3]

#delete stocks last trading day profit normal
data = data[data['last day profit']<0.97]
data = data[data['last day profit'] > 0]

print(data)

output = pd.DataFrame()
'''
#create output file with all stock next day average profit
output['all stocks next day average profit'] = data.groupby('date')['next day profit'].mean()
output.to_csv(dir+'daily strategy/daily profit output.csv')
'''

'''
# define buy and sell indicator
options = ['None'] * len(data)
data = data.sort_values(by=['stock','date'])
for i in range(3,len(data)):
    if data.iloc[i]['1st time being 10 days high'] == 1:
        if data.iloc[i-1]['1st time being 10 days high'] == 1:
            if data.iloc[i-2]['1st time being 10 days high'] == 1:
                if data.iloc[i-2]['above 10 days max vol'] == 1:
                    print(data.iloc[i]['stock'])
                    print(data.iloc[i-1]['stock'])
                    print(data.iloc[i-2]['stock'])
                    if data.iloc[i]['stock'] == data.iloc[i-1]['stock'] and data.iloc[i]['stock'] == data.iloc[i-2]['stock']:
                        options[i] = 'buy'
                        print('buy ' + data.iloc[i]['date'] + ' ' + data.iloc[i]['stock'] )
                        curren_date = data.iloc[i]['date']
                        for j in range(i+1,len(data)):
                            if data.iloc[j]['date'][:2] != curren_date[:3] or data.iloc[j]['date'][6:] != curren_date[6:] or \
                                data.iloc[j]['stock'] != data.iloc[i]['stock']:
                                options[j] = 'sell'
                                break
                            else:
                                if data.iloc[j]['close'] < data.iloc[i]['close'] * 0.9:
                                    options[j] = 'sell'
                                    break
                                else:
                                    options[j] = 'keep'
data['option'] = options
'''

# add column how many stocks are history highest today
output['new highest stocks amount'] = data.groupby('date')['stock'].count()

#add a column trading value = volume * price, select stock by top 5 minimum trading value
data['trading value'] = data['volume'] * data['close']
data['trading value rank'] = data.groupby('date')['trading value'].rank()
data = data[data['trading value rank'] <= 5]

#remove data with big vol
data = data[data['above 10 days max vol'] == 0]

#create another file including data with all indicators
data.to_csv(dir+'history highest price strategy/daily data with new indicators.csv')

#get mean profit of the selected stocks
output['selected stocks next day average profit'] = data.groupby('date')['next day profit'].mean()
output.replace(np.nan, 0, inplace=True)

output.to_csv(dir+'history highest price strategy/daily profit output.csv')

# add list of selected stocks name and their mean profit into the output file; get the total cumprod profit of all stocks and selected stocks
data['stock'] = data['stock'].astype(str)
output['stocks names'] = data.groupby('date')['stock'].agg(lambda col: ' '.join(col))

#output['line_allstock_totalprofit'] = (output['all stocks next day average profit'] + 1).cumprod()
output['line_selectedstock_totalprofit'] = (output['selected stocks next day average profit'] + 1-0.003).cumprod()
output.to_csv(dir+'history highest price strategy/daily profit output.csv')

#print final total profit, compare all stock profit and selected stock profit:
#print('final all stocks profit: ', output['line_allstock_totalprofit'][-1]*100,'%')
print('final selected stocks profit: ', output['line_selectedstock_totalprofit'][-1]*100,'%')

#plot
#plt.plot(output['line_allstock_totalprofit'])
fig = plt.figure(figsize=(40.0,10.0))
fig1 = fig.add_subplot(211)
fig1.plot(output['line_selectedstock_totalprofit'])
fig1.set_title('profit in year ' + year)
fig2 = fig.add_subplot(212)
fig2.plot(output['new highest stocks amount'])
fig2.set_title('new high stocks amount in ' + year)
#fig2.set_xticks(output['date'])
plt.show()
plt.savefig('/Users/clienttest/Documents/Christine/projects/history highest price strategy/history highest strategy profit '+ year + '.png')
plt.close('all')
#plt.legend(loc='best')


