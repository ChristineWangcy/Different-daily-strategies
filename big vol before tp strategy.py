__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np

dir = '/Users/clienttest/Documents/Christine/projects/'

data = pd.read_csv(dir+'big vol before tp strategy/all daily data2.csv')

#del data['date']
data.rename(columns = {data.columns[0]:'date'},inplace=True)
'''
dates = []
for d in data['date']:
    dates.append(d.strip(' 0:00'))
'''
# sort by date and stock symbol
data.sort_values(by=['date','stock'],inplace=True)

# every year
year = '2010'
data = data[pd.to_datetime(data['date']) >= pd.to_datetime(year + '0101')]
data = data[pd.to_datetime(data['date']) < pd.to_datetime(str(int(year)+1) + '0101')]

print(data)

data = data[data['buy']>0]
output = pd.DataFrame()

# add column how many stocks are history highest today
output['new buy stocks amount'] = data.groupby('date')['stock'].count()

#add a column trading value = volume * price, select stock by top 5 minimum trading value
data['trading value'] = data['volume'] * data['close']
data['trading value rank'] = data.groupby('date')['trading value'].rank()
data = data[data['trading value rank'] <= 5]

#create another file including data with all indicators
data.to_csv(dir+'big vol before tp strategy/daily data with new indicators.csv')

#get mean profit of the selected stocks
output['selected stocks next day average profit'] = data.groupby('date')['next day profit'].mean()
output.replace(np.nan, 0, inplace=True)

output.to_csv(dir+'big vol before tp strategy/daily profit output.csv')

# add list of selected stocks name and their mean profit into the output file; get the total cumprod profit of all stocks and selected stocks
data['stock'] = data['stock'].astype(str)
output['stocks names'] = data.groupby('date')['stock'].agg(lambda col: ' '.join(col))

#output['line_allstock_totalprofit'] = (output['all stocks next day average profit'] + 1).cumprod()
output['line_selectedstock_totalprofit'] = (output['selected stocks next day average profit'] + 1-0.003).cumprod()
num = len(output)
max_drawdown = [0] * num
totalprofit = output['line_selectedstock_totalprofit']
for i in range(1,num-1):
    max_drawdown[i] = (min(totalprofit[i+1:]) - totalprofit[i])/totalprofit[i]
output['max drawdown'] = max_drawdown

output.to_csv(dir+'big vol before tp strategy/daily profit output.csv')

#print final total profit, compare all stock profit and selected stock profit:
#print('final all stocks profit: ', output['line_allstock_totalprofit'][-1]*100,'%')
print('final selected stocks profit: ', output['line_selectedstock_totalprofit'][-1]*100,'%')
print('max drowdown is: ', min(output['max drawdown']))

#plot
#plt.plot(output['line_allstock_totalprofit'])
fig = plt.figure(figsize=(40.0,15.0))
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
#fig2.set_xticks(output['date'])
plt.show()
plt.savefig('/Users/clienttest/Documents/Christine/projects/big vol before tp strategy/big vol before tp strategy profit '\
            + year + '.png')
plt.close('all')
#plt.legend(loc='best')


