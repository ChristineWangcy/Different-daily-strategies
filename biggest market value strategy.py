__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np


dir = '/Users/clienttest/Documents/Christine/projects/'

data = pd.read_csv('weekly all data.csv')
del data['date']
data.rename(columns = {data.columns[0]:'date'},inplace=True)

# sort by date and stock symbol
data.sort_values(by=['date','stock'],inplace=True)

#delete trading time too early before 2006
data = data[pd.to_datetime(data['date']) > pd.to_datetime('20060101')]

#delete stocks not traded in last day
data = data[data['trading'] != 0]

#delete stocks trading days < 10 in a week
data = data[data['trading days'] > 3]

#delete stocks last trading day profit > 9.7%
data = data[data['last day profit']<0.097]
print(data)

#output another file with all stock next week average profit
output = pd.DataFrame()
output['all stocks next week average profit'] = data.groupby('date')['next week profit'].mean()
output.to_csv('weekly profit output.csv')

#add a column trading value = volume * price
data['trading value'] = data['volume'] * data['close']
data['trading value rank'] = data.groupby('date')['trading value'].rank()

#selet top 10 minimum trading value stock
data = data[data['trading value rank'] <= 5]
print(data)

output['selected stocks next week average profit'] = data.groupby('date')['next week profit'].mean()
output.to_csv('weekly profit output.csv')
data.to_csv('weekly data with trading value rank.csv')

# add stocks name to output file
data['stock'] = data['stock'].astype(str)
output['stocks names'] = data.groupby('date')['stock'].agg(lambda col: ' '.join(col))
output['line_allstock_totalprofit'] = (output['all stocks next week average profit'] + 1-0.001).cumprod()
output['line_selectedstock_totalprofit'] = (output['selected stocks next week average profit'] + 1-0.001).cumprod()
output.to_csv('weekly profit output.csv')

#print final total profit:
print('final all stocks profit: ', output['line_allstock_totalprofit'][-1]*100,'%')
print('final selected stocks profit: ', output['line_selectedstock_totalprofit'][-1]*100,'%')

#plot
plt.plot(output['line_allstock_totalprofit'])
plt.plot(output['line_selectedstock_totalprofit'])
plt.legend(loc='best')
plt.show()

