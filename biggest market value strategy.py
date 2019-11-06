__author__ = 'clienttest'

import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import numpy as np


dir = '/Users/clienttest/Documents/Christine/projects/biggest market value strategy'

data = pd.read_csv('data files/allstock data in one file/monthly all data.csv')
del data['date']
data.rename(columns = {data.columns[0]:'date'},inplace=True)

# sort by date and stock symbol
data.sort_values(by=['date','stock'],inplace=True)

#delete trading time too early before 2006
data = data[pd.to_datetime(data['date']) > pd.to_datetime('20060101')]

#delete stocks not traded in last day
data = data[data['trading'] != 0]

#delete stocks trading days < 10 in a month
data = data[data['trading days'] > 3]

#delete stocks last trading day profit > 9.7%
data = data[data['last day profit']<0.097]
print(data)

#create output file with all stock next month average profit
output = pd.DataFrame()
output['all stocks next month average profit'] = data.groupby('date')['next month profit'].mean()
output.to_csv('biggest market value strategy/monthly profit output.csv')

#add a column trading value = volume * price, select stock by top 5 minimum trading value
data['trading value'] = data['volume'] * data['close']
data['trading value rank'] = data.groupby('date')['trading value'].rank()
data = data[data['trading value rank'] <= 20]

#create another file including data with all indicators
data.to_csv('biggest market value strategy/monthly data with all indicators.csv')

#get mean profit of the selected stocks
output['selected stocks next month average profit'] = data.groupby('date')['next month profit'].mean()
output.to_csv('biggest market value strategy/monthly profit output.csv')


# add list of selected stocks name and their mean profit into the output file; get the total cumprod profit of all stocks and selected stocks
data['stock'] = data['stock'].astype(str)
output['stocks names'] = data.groupby('date')['stock'].agg(lambda col: ' '.join(col))
output['line_allstock_totalprofit'] = (output['all stocks next month average profit'] + 1-0.001).cumprod()
output['line_selectedstock_totalprofit'] = (output['selected stocks next month average profit'] + 1-0.001).cumprod()
output.to_csv('biggest market value strategy/monthly profit output.csv')

#print final total profit, compare all stock profit and selected stock profit:
print('final all stocks profit: ', output['line_allstock_totalprofit'][-1]*100,'%')
print('final selected stocks profit: ', output['line_selectedstock_totalprofit'][-1]*100,'%')

#plot
plt.plot(output['line_allstock_totalprofit'])
plt.plot(output['line_selectedstock_totalprofit'])
plt.legend(loc='best')
plt.show()

