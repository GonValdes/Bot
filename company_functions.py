# -*- coding: utf-8 -*-
"""
Created on Sun May  2 15:51:23 2021

@author: gonza
"""


#############################################################
### Technical


import pandas as pd
import matplotlib.pyplot as plt
import os
import glob
import numpy as np
from datetime import datetime,  timedelta
import investpy
from pandas_datareader.data import DataReader
import requests
from bs4 import BeautifulSoup

work_path = 'C:\\Users\\gonza\\OneDrive\\Escritorio\\BOLSA\\Current'
os.chdir(work_path)
import FearAndGreed as FaG

### Define relevant dates
today_date = datetime.today().strftime('%d/%m/%Y')


### Define functions
def time_ago(n_days):
    date_ago = (datetime.today() - timedelta(days = n_days )).strftime('%d/%m/%Y')
    return date_ago

def get_stock_data(ticker,place,from_d,to_d):
    data = investpy.get_stock_historical_data(stock=ticker,
                                        country = place,
                                        from_date = from_d,
                                        to_date = to_d)
    return data

def get_upsNdown(stock_data,days):
    max_ndays = max(stock_data.iloc[(stock_data.index > time_ago(days)),1])
    min_ndays = min(stock_data.iloc[(stock_data.index > time_ago(days)),2])
    
    up_from_min = (stock_data.iloc[-1,3]/min_ndays -1)*100 
    down_from_max = (1- stock_data.iloc[-1,3]/max_ndays)*100
    if up_from_min<0:
        up_from_min = '-'
    if down_from_max<0:
        down_from_max= '-'
    return [up_from_min,down_from_max]

def get_up_down_table(stock_data):
    [up_1y,down_1y] = get_upsNdown(stock_data,365)
    [up_6m,down_6m] = get_upsNdown(stock_data,30*6)
    [up_3m,down_3m] = get_upsNdown(stock_data,30*3)
    [up_1m,down_1m] = get_upsNdown(stock_data,30)
    [up_2w,down_2w] = get_upsNdown(stock_data,14)
    [up_1w,down_1w] = get_upsNdown(stock_data,7)

    up_down = ([up_1w,up_2w,up_1m,up_3m,up_6m,up_1y],
           [down_1w,down_2w,down_1m,down_3m,down_6m,down_1y])
    up_down_table = pd.DataFrame(up_down,columns=['1w','2w','1m','3m','6m','1y'],
                                 index=['up from min','down from max'])
    return up_down_table

def get_bond_data(years, from_d, to_d):
    data = investpy.bonds.get_bond_historical_data(bond='U.S. '+str(years)+'Y',
                                               from_date = from_d,
                                               to_date= to_d)
    return data

def get_index_data(ticker,place,from_d,to_d):
    data = investpy.indices.get_index_historical_data(index=ticker,
                                        country = place,
                                        from_date = from_d,
                                        to_date = to_d)
    return data

def get_yield_curve(from_d, to_d):
    yield_curve = []
    years = [1,2,3,5,10,30]
    for year in years:
        yield_curve.append(get_bond_data(year, from_d, to_d).iloc[-1,-1])
    return yield_curve

def get_fred_data(series_code ,start):
    data_source = 'fred'
    data = DataReader(series_code,data_source, start)
    return data

def get_fearandgreed():
    url = 'https://money.cnn.com/data/fear-and-greed/'
    resp = requests.get(url).content
    soup = BeautifulSoup(resp, 'html.parser')
    chart = soup.find('div',{'id':'needleChart'})
    fg = chart.find('li').text
    fg = fg.replace('Fear & Greed Now: ', '').split(' ')[0]
    return fg

def get_fearandgreed_historical(work_path):
    FaG.update()
    data = pd.read_csv(work_path+'\\'+'PGdata.txt', delimiter = " ")
    data['Date'] = pd.to_datetime(data['Date'],format='%Y%m%d')
    data.set_index('Date', inplace=True)
    return data


ticker =  'AAPL'
country = 'United States'
from_date = time_ago(365*2)
to_date = today_date
stock_data = get_stock_data(ticker,country,from_date,to_date)

# Bajadas
days_observed = 365 # In the chart

mask = (stock_data.index > time_ago(365*2))

up_down_table = get_up_down_table(stock_data)
up_down_table



color_list = ['#85DB00','#00987A','#0300ff']
windows_list = [50,125,200]

plt.plot(stock_data.iloc[(stock_data.index > time_ago(days_observed)),3], '-',
         linewidth=1, color= 'k')
for x in range(3):
    SMA_data = stock_data.iloc[:,3].rolling(window=windows_list[x]).mean()
    plt.plot(SMA_data.iloc[SMA_data.index > time_ago(days_observed)], 
             label='SMA{0}'.format(windows_list[x]),
             linewidth=0.6, color = color_list[x])
    plt.legend()
plt.grid()




datetime.strptime(time_ago(days_observed), '%m-%Y')






import re
import json

url= 'http://financials.morningstar.com/ratios/r.html?t=amzn&region=usa&culture=en-US'

resp = requests.get(url).content
soup = BeautifulSoup(resp, 'html.parser')
chart = soup.find('div')
fg = chart.find('li').text
fg = fg.replace('Fear & Greed Now: ', '').split(' ')[0]

soup = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url).text)[0])['componentData'], 'lxml')

json.loads(re.findall(r'xxx\((.*)\)', requests.get(url).text)[0])['componentData']

url1 = 'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t=AAPL'
url2 = 'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t=AAPL'

soup1 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url1).text)[0])['componentData'], 'lxml')
soup2 = BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(url2).text)[0])['componentData'], 'lxml')

def morningstar_financial(soup):
    data_matrix = []
    for i, tr in enumerate(soup.select('tr')):
        row_data = [td.text for td in tr.select('td, th') if td.text]   
        
        if not row_data:
            continue
        if len(row_data) < 12:
            header = row_data
            continue
        data_matrix.append(row_data)
    data_matrix = pd.DataFrame(np.array(data_matrix))
    data_matrix = data_matrix.set_index(0)
    data_matrix.columns= header
    return data_matrix

def morningstar_ratios(soup):
    data_matrix = []
    header = []
    for i, tr in enumerate(soup.select('tr')):
        row_data = [td.text for td in tr.select('td, th') if td.text]   
        print(row_data)
        if not row_data:
            continue
        if len(row_data) < 12:
            header.append(row_data)
            continue
        data_matrix.append(row_data)
    data_matrix = pd.DataFrame(np.array(data_matrix))
    data_matrix = data_matrix.set_index(0)
    # data_matrix.columns= header
    return data_matrix, header
    
        
data = morningstar_financial(soup1)
data2, header = morningstar_ratios(soup2)




### Previous code
# def SMA(stock_data,days_observed,mean_horizon):
#     #mean_horizon = days evaluated. i.e. 50 for SMA50
#     SMeanA = pd.DataFrame([])
#     for i in stock_data.iloc[stock_data.index > time_ago(days_observed),3].index:
#         f_date = np.where(stock_data.index == i)[0][0]
#         in_date = f_date - mean_horizon
#         aux = pd.DataFrame({'Date':i ,'SMA' :[stock_data.iloc[in_date:f_date,3].mean() ]})
#         aux.set_index('Date', inplace=True)
#         SMeanA = SMeanA.append(aux)
#     return SMeanA

     #SMA_d = {}
#for x in [50,125,125]:
    #SMA_d["{0}".format(x)] = SMA(stock_data,days_observed,x) #SMA_d['50']   