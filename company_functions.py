"""
Created on Apr 2021

@author: Gonzalo Valdés
mail:gonzalovaldescernuda@gmail.com

Script to obtain different company valuation metrics and obtain the plots.
"""
#############################################################

import pandas as pd
import matplotlib.pyplot as plt
import os
import numpy as np
import re
import json
from datetime import datetime,  timedelta
import investpy
from pandas_datareader.data import DataReader
import requests
from bs4 import BeautifulSoup
import FearAndGreed as FaG
from pathlib import Path
from scipy.stats.mstats import gmean


work_path = os.getcwd()


#Define figure size and quality          
figure_size = [9,4.8]
dpi_num = 100
### Define relevant dates
today_date = datetime.today().strftime('%d/%m/%Y')

### Define functions
def time_ago(n_days,format):
    #Obtain date for n_days ago in the desired format
    #format 0: d/m/y; 1:y-m-d;
    formats = ['%d/%m/%Y','%Y-%m-%d','%d-%m-%Y']
    date_ago = (datetime.today() - timedelta(days = n_days )).strftime(formats[format])

    return date_ago

def get_stock_data(ticker,place,from_d,to_d):
    #Obtain stock data using investpy. Time period : [from_d,to_d]
    data = investpy.get_stock_historical_data(stock=ticker,
                                        country = place,
                                        from_date = from_d,
                                        to_date = to_d)
    return data

def get_upsNdown(stock_data,days):
    #Obtain variation from minimum and maximum point since days ago
    max_ndays = max(stock_data.iloc[(stock_data.index > time_ago(days,1)),1])
    min_ndays = min(stock_data.iloc[(stock_data.index > time_ago(days,1)),2])
    
    up_from_min = round((stock_data.iloc[-1,3]/min_ndays -1)*100,1)
    down_from_max = round((1- stock_data.iloc[-1,3]/max_ndays)*100,1)
    if up_from_min<0:
        up_from_min = '-'
    if down_from_max<0:
        down_from_max= '-'
    return [up_from_min,down_from_max]

def get_up_down_table(stock_data):
    #Creation of a table with ups and downs from different time horizons
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
    #Obtain stock data using investpy. Time period : [from_d,to_d]
    #Obtain bond data using investpy. Time period : [from_d,to_d]
    data = investpy.bonds.get_bond_historical_data(bond='U.S. '+str(years)+'Y',
                                               from_date = from_d,
                                               to_date= to_d)
    return data

def get_index_data(ticker,place,from_d,to_d):
    #Obtain index data using investpy. Time period : [from_d,to_d]
    data = investpy.indices.get_index_historical_data(index=ticker,
                                        country = place,
                                        from_date = from_d,
                                        to_date = to_d)
    return data

def get_yield_curve(from_d, to_d):
    #Obtain yield curve data for a time interval
    yield_curve = []
    years = [1,2,3,5,10,30]
    for year in years:
        yield_curve.append(get_bond_data(year, from_d, to_d).iloc[-1,-1])
    return yield_curve

def get_fred_data(series_code ,start):
    #Obtain data using fred api since start date
    data_source = 'fred'
    data = DataReader(series_code,data_source, start)
    return data

def get_fearandgreed():
    #Use beautiful soup to extract fear and greed
    url = 'https://money.cnn.com/data/fear-and-greed/'
    resp = requests.get(url).content
    soup = BeautifulSoup(resp, 'html.parser')
    chart = soup.find('div',{'id':'needleChart'})
    fg = chart.find('li').text
    fg = fg.replace('Fear & Greed Now: ', '').split(' ')[0]
    return fg

def get_fearandgreed_historical(work_path):
    #Update fearandgreed historical data. Historical data is saved in a txt file
    FaG.update()
    data = pd.read_csv(work_path+'\\'+'PGdata.txt', delimiter = " ")
    data['Date'] = pd.to_datetime(data['Date'],format='%Y%m%d')
    data.set_index('Date', inplace=True)
    return data

def get_stock_data_weekly(stock_data,days_observed):
    #Provide a Dataframe with weekly closing prices
    #Obtain next friday
    friday = datetime.today()
    while friday.weekday() != 4:
        friday += timedelta(1)
    #Get list of fridays till timeframe limit
    friday_list = []
    while friday > datetime.strptime(time_ago(days_observed+52*7,0), '%d/%m/%Y'):
        friday_list.append(friday.strftime('%Y-%m-%d'))
        friday -= timedelta(7)
    #Get friday values
    stock_data_weekly = []
    date = []
    for i in friday_list:
        # stock_data.iloc[stock_data.index == i,3]
        try:
            stock_data_weekly.append(stock_data.iloc[stock_data.index == i,3][0])
            date.append(i)
        except:
            continue
    #Provide a Dataframe with weekly closing price
    stock_data_weekly = pd.DataFrame(stock_data_weekly[::-1])
    stock_data_weekly = stock_data_weekly.set_axis(pd.to_datetime(date[::-1]), inplace=False).set_axis(['Week close'], axis=1, inplace=False)   
    return stock_data_weekly

def get_rscm(stock_data,sp500_data,days_observed):
    #Obtain RSCM mansfield indicator. Shows momentum of the price.
    rscm =  get_stock_data_weekly(stock_data,days_observed+52*7)
    sp500_weekly = get_stock_data_weekly(sp500_data,days_observed+52*7)
    rscm['RSD'] = rscm['Week close']/sp500_weekly['Week close']
    rscm['RSCM'] = ((rscm['RSD']/abs(rscm['RSD'].rolling(window=52).mean()))-1)*100
    return rscm['RSCM'].iloc[rscm.index > time_ago(days_observed,1)]

def plt_stock_sma(stock_data, days_observed,figure_size):
    color_list = ['#85DB00','#00987A','#0300ff']
    windows_list = [50,125,200]
    
    plt.figure(figsize=figure_size,dpi=150)
    
    plt.plot(stock_data.iloc[(stock_data.index > time_ago(days_observed,1)),3], '-',
             linewidth=1, color= 'k')
    for x in range(3):
        SMA_data = stock_data.iloc[:,3].rolling(window=windows_list[x]).mean()
        plt.plot(SMA_data.iloc[SMA_data.index > time_ago(days_observed,1)], 
                 label='SMA{0}'.format(windows_list[x]),
                 linewidth=0.7, color = color_list[x])
        plt.legend()
    plt.grid()

def morningstar_financial(soup,n):
    #Function to read soup generated by morningstar
    #n -> [Valuation, Financials, Key ratios]
    data_matrix = []
    header = []
    for i, tr in enumerate(soup.select('tr')):
        row_data = [td.text for td in tr.select('td, th') if td.text]   
        
        if not row_data:
            continue
        if len(row_data) < 12:
            if n==2:
                header.append(row_data)
            else:
                header = row_data
            continue
        data_matrix.append(row_data)
    data_matrix = pd.DataFrame(np.array(data_matrix))
    if n != 0:
        data_matrix = data_matrix.set_index(0)
    # if n == 1:
    #     data_matrix.columns= header
    return data_matrix

def get_plot_ydata(data,row,initial_column,new_value):
    #Obtain the Y values for each plot
    #data: dataset in which the values are found. new_value is the substitute in case of no value or NaN
    Y=[]
    for index,value in enumerate(data.iloc[row,initial_column:].tolist()):
        if value == '—':
            Y.append(new_value)
        else:
            Y.append(float(value.replace(',','')))
    return Y

def get_ev_fcf(stock_data,data_financials,years):
    #Function to obtain the ev/fcf ratio from morningstar data
    #1:calculate market cap.2:Obtain total assets.3:Obtain cash and liabilities
    #Define the years the price calculation
    years_clean = [int(year[0:4]) for year in years.iloc[:-1]]
    share_price = []
    for year in years_clean:
        share_price.append(np.mean(stock_data.iloc[(stock_data.index > datetime(year, 9, 1))&(stock_data.index < datetime(year, 9, 30)) ,3]))
    share_price.append(np.mean(stock_data.iloc[(stock_data.index > time_ago(7,1)) ,3]))
    #Obtain market cap
    shares = np.multiply(get_plot_ydata(data_financials["Financials"],8,0,0),10**6)
    market_cap = np.multiply(np.array(share_price),shares)
     
    # bv_share = get_plot_ydata(data_financials["Financials"],9,0,0)[:-1] 
    # total_equity = np.multiply(shares,bv_share)
    # equity_div_total = np.multiply(get_plot_ydata(data_financials["Key ratios"],-16,0,0)[:-1],0.01)
    #Extract required data and ratios
    net_income = np.multiply(get_plot_ydata(data_financials["Financials"],4,0,0),10**6)
    roa = np.multiply(get_plot_ydata(data_financials["Key ratios"],14,0,0),0.01) 
    liabilities_div_total = np.multiply(get_plot_ydata(data_financials["Key ratios"],-17,0,0),0.01) 
    cash_div_total = np.multiply(get_plot_ydata(data_financials["Key ratios"],-34,0,0) ,0.01)
    
    #Obtain assets, cash and liabilities
    # total_assets = np.divide(total_equity,equity_div_total)
    total_assets = np.divide(net_income,roa)
    cash =  np.multiply(total_assets,cash_div_total)
    liabilities =  np.multiply(total_assets,liabilities_div_total)
    #finally obtain yearly enterprise valuation and ev/fcf (at September of each year)
    enterprise_valuation = market_cap+liabilities-cash
    ev_fcf = np.divide(enterprise_valuation,np.multiply(get_plot_ydata(data_financials["Financials"],12,0,0),10**6))
    ev_inc = np.divide(enterprise_valuation,net_income)
    return ev_fcf,ev_inc,market_cap[-1]

def get_yearly_growth(stock_data,years):
    #Calculate growth for the demanded years and the geometric mean(last value)
    growth = []
    years_clean = [int(year[0:4]) for year in years.iloc[:-1]]
    for year in  years_clean:
        try:
            initial_value = []
            final_value = []
            #This serves to obtain a value in case stock market was closed 
            for day in list(range(1,6)):
                if not not initial_value:
                    continue
                try:
                    initial_value = float(stock_data.iloc[stock_data.index == datetime(year, 1, day) , 3])
                except:
                    continue
                
            for day in list(range(27,32))[::-1]:
                if not not final_value:
                    continue
                try:
                    final_value = float(stock_data.iloc[stock_data.index == datetime(year, 12, day) , 3])
                except:
                    continue
            growth.append(final_value/initial_value)
        except:
            growth.append('NA')
    #Calculate geometric average of every value
    growth.append(float(gmean(list(map(growth.__getitem__, 
                [i for i, x in enumerate([type(value)==float for value in growth]) if x])))))
    #Standarise values and return them
    growth_standarised = list(map(lambda value: round((value-1)*100)
                                  if type(value)==float else (0),growth))
    return growth_standarised
    
def get_std(stock_data):
    #Get standard deviation for stock data
    daily_growth = [1]
    for i in range(1,len(stock_data)):
        daily_growth.append(stock_data.iloc[i,3]/stock_data.iloc[i-1,3])
    standard_deviation = np.std(daily_growth)
    return standard_deviation

def get_RSI(stock_data):
    #Obtain RSI indicator
    daily_growth = [0]
    for i in range(1,len(stock_data)):
        daily_growth.append(stock_data.iloc[i,3]-stock_data.iloc[i-1,3])
    
    df = pd.DataFrame()
    df['growth'] = daily_growth
    #Get ups and down  
    df['ups'] = df.apply(lambda x: x['growth'] if x['growth']>=0 else 0, axis=1)
    df['downs'] = df.apply(lambda x: abs(x['growth']) if x['growth']<0 else 0, axis=1)

    #Average ups and downs
    df['avg ups'] = df['ups'].rolling(14).mean()
    df['avg downs'] = df['downs'].rolling(14).mean()
    df['RSI'] = 100 - 100/(1+(df['avg ups']/df['avg downs']))
    return df['RSI'].values.tolist()
    
    
###############################################################################
###############################################################################
###############################################################################
###############################################################################
def get_company_data(ticker, country):
    #This function performs all the data analysis and chart generation
    ############################################################################
    ############################################################################
    ###Technical analysis
    Path(work_path+'\\company_images').mkdir(parents=True, exist_ok=True)
    os.chdir(work_path+'\\company_images')
    
    from_date = time_ago(365*11,0)
    to_date = today_date
    stock_data = get_stock_data(ticker,country,from_date,today_date)
    sp500_data = get_index_data('S&P 500','United States',from_date,to_date)
    
    #Ups and down from minimum and maximum
    up_down_table = get_up_down_table(stock_data)
    
    #Fear and greed values
    fag = get_fearandgreed()
    #VIX
    VIX = get_fred_data('VIXCLS',time_ago(7, 1)).iloc[-1].values.tolist()
    #Obtain daily std deviation of growth    
    stock_std = round(get_std(stock_data)*100,1)
    stock_std_y = round(get_std(stock_data[-252:])*100,1)
    sp500_std =round(get_std(sp500_data)*100,1)
    sp500_std_y = round(get_std(sp500_data[-252:])*100,1)
    #Generate RSI technical indicator
    stock_data['RSI'] = get_RSI(stock_data)
    ############################################################################
    ############################################################################
    ###Fundamental analyisis
    
    # Path(work_path+'\\fundamental_images').mkdir(parents=True, exist_ok=True)
    # os.chdir(work_path+'\\fundamental_images')
    #Get data from morningstar via web scrapping
    #[Valuation, Financials, Key ratios]
    data_name = ['Valuation', 'Financials', 'Key ratios'] 
    #Provide urls for each of the morningstar datasets
    urls = ['https://financials.morningstar.com/valuate/valuation-history.action?&t=XNAS:'+ticker+'&region=usa&culture=en-US&cur=&type=price-earnings',
            'http://financials.morningstar.com/finan/financials/getFinancePart.html?&callback=xxx&t='+ticker,
            'http://financials.morningstar.com/finan/financials/getKeyStatPart.html?&callback=xxx&t='+ticker]
    #Obtain soups
    soups = [BeautifulSoup(requests.get(urls[0]).content, 'html.parser'),
             BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(urls[1]).text)[0])['componentData'], 'lxml'),
             BeautifulSoup(json.loads(re.findall(r'xxx\((.*)\)', requests.get(urls[2]).text)[0])['componentData'], 'lxml')]
    #Obtain datasets
    data_financials = {}
    for index,soup in enumerate(soups):
        data_financials[data_name[index]] = morningstar_financial(soup,index)
        
    
    #Year names generation for the charts
    years = data_financials["Key ratios"].iloc[0,0:]
    years_names = []
    for i,year in enumerate(years): 
        if year[0].isnumeric():
            years_names.append(year[2:4])
        else:
            years_names.append(year)
     
    #Obtain EV/FCF and EV/income ratios
    ev_fcf,ev_inc,market_cap = get_ev_fcf(stock_data,data_financials,years)
    
    #Obtain stock growth relative to the market
    stock_growth = get_yearly_growth(stock_data,years)
    sp500_growth = get_yearly_growth(sp500_data,years)
    
    #Years value for plots
    years_clean = [int(year[0:4]) for year in years.iloc[:-1]]
    share_price = []
    for year in years_clean:
        share_price.append(np.mean(stock_data.iloc[(stock_data.index > datetime(year, 9, 1))&(stock_data.index < datetime(year, 9, 30)) ,3]))
    share_price.append(np.mean(stock_data.iloc[(stock_data.index > time_ago(7,1)) ,3]))
    
    ###########################################################################
    ##########################################################################
    ###Start plotting
    
    #Ups and down from minimum and maximum
    cell_text = up_down_table.values.tolist()
    column_labels = ['1w','2w','1m','3m','6m','1y']
    row_labels = ['Up from min(%)','Down from max(%)']
    
    plt.figure(dpi=dpi_num)
    plt.table(cellText=cell_text, cellLoc='center', 
                             rowLabels=row_labels,colLabels=column_labels, colColours=None, 
                            colLoc='center', loc='center', edges='closed')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    plt.tight_layout()
    plt.savefig('set3_2_1.png')
    
    #Technical charts
    #Charts with MA
    plt_stock_sma(stock_data, 365,figure_size)
    plt.savefig('set3_1_1.png')
    plt_stock_sma(stock_data,365*10,figure_size )
    plt.savefig('set3_2_1.png')
    
    #Analyse momentum with RSC Mansfield
    plt.figure(dpi=dpi_num)
    rscm = get_rscm(stock_data,sp500_data,365)
    plt.plot(rscm,color='k')
    plt.fill_between(rscm.index, 0,rscm, where=rscm>0, interpolate=True,color='g')
    plt.fill_between(rscm.index, 0,rscm, where=rscm<0, interpolate=True,color='r')
    plt.title('RSCM')
    plt.savefig('set3_1_3.png')
    
    plt.figure(dpi=dpi_num)
    rscm = get_rscm(stock_data,sp500_data,365*10)
    plt.plot(rscm,color='k')
    plt.fill_between(rscm.index, 0,rscm, where=rscm>0, interpolate=True,color='g')
    plt.fill_between(rscm.index, 0,rscm, where=rscm<0, interpolate=True,color='r')
    plt.title('RSCM')
    plt.savefig('set3_2_2.png')
    
    #RSI
    plt.figure(dpi=dpi_num)
    x_horizon = stock_data.index[stock_data.index>time_ago(365,1)]
    plt.plot(stock_data['RSI'][stock_data.index>time_ago(365,1)],color='k')
    plt.plot(x_horizon, [70] * len(x_horizon), label="overbought",color='g')
    plt.plot(x_horizon, [30] * len(x_horizon), label="overbought",color='r')
    plt.title('RSI')
    plt.savefig('set3_1_2.png')
    
    #Table with FG, VIX and Std
    cell_text = [[str(round(float(fag))),''],[str(round(VIX[0])),''],
                 [str(stock_std),str(stock_std_y)],[str(sp500_std),str(sp500_std_y)]]
    row_labels = ['F&G','VIX','{0} std'.format(ticker),'S&P500 std']
    column_labels = ['All','Yearly']

    plt.figure(dpi=dpi_num)
    plt.table(cellText= cell_text, cellLoc='center', 
                             rowLabels=row_labels,colLabels=column_labels, colColours=None, 
                            colLoc='center', loc='center', edges='closed')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    plt.tight_layout()
    plt.savefig('set3_3_1.png')
    
    #Create a table with growth relative to the market
    years_names_growth = years_names[:-1]
    years_names_growth.append('Avg')
    cell_text = [stock_growth,sp500_growth]
    column_labels = years_names_growth
    row_labels = ['{0}(%)'.format(ticker),'S&P500(%)']

    plt.figure(dpi=dpi_num)
    plt.table(cellText=cell_text, cellLoc='center', 
                             rowLabels=row_labels,colLabels=column_labels, colColours=None, 
                            colLoc='center', loc='center', edges='closed')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    plt.tight_layout()
    plt.savefig('set3_3_2.png')
    
    #Plot Revenue
    Y = get_plot_ydata(data_financials["Financials"],0,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.bar(years_names,Y)
    plt.ylabel('m$')
    plt.title('Revenue')
    plt.savefig('set2_1_1.png')
    
    #Plot income
    X_axis = np.arange(len(years_names))
      
    Y1 = get_plot_ydata(data_financials["Financials"],2,0,0)
    Y2 = get_plot_ydata(data_financials["Financials"],4,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.bar(X_axis - 0.2, Y1, 0.4, label = 'Oper')
    plt.bar(X_axis + 0.2, Y2, 0.4, label = 'Net')
    plt.xticks(X_axis, years_names)
    plt.ylabel("m$")
    plt.title("Operating and net income")
    plt.legend()
    plt.savefig('set2_1_2.png')
    
    #Plot Cash flow
    Y1 = get_plot_ydata(data_financials["Financials"],10,0,0)
    Y2 = get_plot_ydata(data_financials["Financials"],12,0,0)
    Y3 = get_plot_ydata(data_financials["Financials"],11,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.bar(X_axis - 0.2, Y1, 0.2, label = 'Oper')
    plt.bar(X_axis + 0, Y2, 0.2, label = 'Free')
    plt.bar(X_axis + 0.2, [-y for y in Y3], 0.2, label = 'CapEx')
    plt.xticks(X_axis, years_names)
    plt.ylabel("m$")
    plt.title("Operating and Free Cash Flow")
    plt.legend()
    plt.savefig('set2_1_3.png')
    
    
    #EPS - FCF/share - Recompras 
    Y = get_plot_ydata(data_financials["Financials"],5,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y,label='EPS')
    Y2 = get_plot_ydata(data_financials["Financials"],13,0,0)
    plt.plot(years_names[:],Y2)
    plt.scatter(years_names[:],Y2,label='FCF/Share')
    plt.grid()
    plt.legend()
    plt.title("EPS and FCF/Share")
    plt.savefig('set2_4_3.png')
    
    Y = get_plot_ydata(data_financials["Financials"],8,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y)
    plt.grid()
    plt.title("Shares")
    plt.savefig('set2_2_3.png')
    
    #PER
    Y = get_plot_ydata(data_financials["Valuation"],1,1,0)
    Y2 = get_plot_ydata(data_financials["Valuation"],2,1,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y,label='{0}'.format(ticker))
    plt.plot(years_names,Y2)
    plt.scatter(years_names,Y2,label='S&P 500')
    plt.grid()
    plt.legend()
    plt.title("PER")
    plt.savefig('set2_3_2.png')
    
    #Price/Book Value
    Y = get_plot_ydata(data_financials["Valuation"],4,1,0)
    Y2 = get_plot_ydata(data_financials["Valuation"],5,1,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y,label='{0}'.format(ticker))
    plt.plot(years_names,Y2)
    plt.scatter(years_names,Y2,label='S&P 500')
    plt.grid()
    plt.legend()
    plt.title("Price/Book Value")
    plt.savefig('set2_3_3.png')
    # plt.savefig('set2_4_3.png')
    
    #Price/Cash flow
    Y = get_plot_ydata(data_financials["Valuation"],10,1,0)
    Y2 = get_plot_ydata(data_financials["Valuation"],11,1,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y,label='{0}'.format(ticker))
    plt.plot(years_names,Y2)
    plt.scatter(years_names,Y2,label='S&P 500')
    plt.grid()
    plt.legend()
    plt.title("Price/Cash Flow")
    plt.savefig('set2_4_2.png')
    
    #EV/FCF
    Y = np.transpose(ev_fcf)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    plt.plot(years_names,Y)
    plt.scatter(years_names,Y,label='{0}'.format(ticker))
    plt.grid()
    plt.title("EV/FCF")
    plt.savefig('set2_3_1.png')
    
    # #EV/net income
    # Y = np.transpose(ev_inc)
    
    # plt.figure(figsize=figure_size,dpi=dpi_num)
    # plt.plot(years_names,Y)
    # plt.scatter(years_names,Y,label='{0}'.format(ticker))
    # plt.grid()
    # plt.title("EV/Net Income")
    # plt.savefig('set2_3_3.png')
    
    #- Quick Ratio(Current liabilities/assets) -Cash ratio(Can current liabilities be paid with cash)
    Y = get_plot_ydata(data_financials["Key ratios"],-12,0,0)
    Y2 = [np.array(get_plot_ydata(data_financials["Key ratios"],-20,0,0))/np.array(get_plot_ydata(data_financials["Key ratios"],-17,0,0))]
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    fig, ax1 = plt.subplots()
    ax1.plot(years_names,Y)
    ax1.scatter(years_names,Y,label='Quick Ratio')
    color = 'C0'
    ax1.set_ylabel('Quick Ratio', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(None)
    ax2 = ax1.twinx()
    color='orange'
    ax2.plot(years_names,np.transpose(Y2), color=color)
    ax2.scatter(years_names,Y2,label='Short/Long term debt', color=color)
    ax2.set_ylabel('Short/Long term debt', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title("Debt/Equity and Short/Long term debt ratio")
    plt.savefig('set2_2_1.png')
    
    #-Debt/Equity(How am I financed) - Short-term/long-term debt
    Y = get_plot_ydata(data_financials["Key ratios"],-10,0,0)
    Y2 = [np.array(get_plot_ydata(data_financials["Key ratios"],-34,0,0))/np.array(get_plot_ydata(data_financials["Key ratios"],-20,0,0))]
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    fig, ax1 = plt.subplots()
    ax1.plot(years_names,Y)
    ax1.scatter(years_names,Y,label='Debt/Equity')
    color = 'C0'
    ax1.set_ylabel('Debt/Equity', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(None)
    ax2 = ax1.twinx()
    color='orange'
    ax2.plot(years_names,np.transpose(Y2), color=color)
    ax2.scatter(years_names,Y2,label='Cash ratio', color=color)
    ax2.set_ylabel('Cash ratio', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title("Short-term Quick Ratio(assets/liabilities) and Cash ratio(cash/liabilities)")
    plt.savefig('set2_2_2.png')
    
    
    #ROE - ROIC
    Y = get_plot_ydata(data_financials["Key ratios"],16,0,0)
    Y2 = get_plot_ydata(data_financials["Key ratios"],17,0,0)
    
    plt.figure(figsize=figure_size,dpi=dpi_num)
    fig, ax1 = plt.subplots()
    ax1.plot(years_names,Y)
    ax1.scatter(years_names,Y,label='ROE')
    color = 'C0'
    ax1.set_ylabel('ROE(%)', color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax1.grid(None)
    ax2 = ax1.twinx()
    color='orange'
    ax2.plot(years_names,Y2, color=color)
    ax2.scatter(years_names,Y2,label='ROIC', color=color)
    ax2.set_ylabel('ROIC(%)', color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title("ROE and ROIC")
    plt.savefig('set2_4_1.png')
    
    #Create a table with the annualized (or 5 years averaged) growth of:
    #Revenue(rev) -Net income(ni) -Operative income(oi) -Cash flow: operating(ocf) and free(fcf) 
    
    rev_1y = get_plot_ydata(data_financials["Key ratios"],19,0,0)[:-1]
    rev_1y.append(round((gmean([x/100+1 for x in rev_1y])-1)*100,1))
    # rev_5y = get_plot_ydata(data_financials["Key ratios"],21,0,0)
    ni_1y = get_plot_ydata(data_financials["Key ratios"],27,0,0)[:-1]
    ni_1y.append(round((gmean([x/100+1 for x in ni_1y])-1)*100,1))
    # ni_5y = get_plot_ydata(data_financials["Key ratios"],29,0,0)
    oi_1y = get_plot_ydata(data_financials["Key ratios"],23,0,0)[:-1]
    oi_1y.append(round((gmean([x/100+1 for x in oi_1y])-1)*100,1))
    # oi_5y = get_plot_ydata(data_financials["Key ratios"],25,0,0)
    ocf_1y = get_plot_ydata(data_financials["Key ratios"],36,0,0)[:-1]
    ocf_1y.append(round((gmean([x/100+1 for x in ocf_1y])-1)*100,1))
    fcf_1y = get_plot_ydata(data_financials["Key ratios"],37,0,0)[:-1]
    fcf_1y.append(round((gmean([x/100+1 for x in fcf_1y])-1)*100,1))
    
    cell_text = [rev_1y,ni_1y,oi_1y,fcf_1y,ocf_1y]        
    column_labels = years_names[:-1]
    column_labels.append('Average')
    row_labels = ['Revenue(%)','Net income(%)','Operating income(%)',
                  'Free Cash Flow(%)','Operating Cash Flow(%)']
    
    cell_color =  [[None]*len(column_labels) for _ in range(len(row_labels))]
    
    for i in range(len(row_labels)):
        for j in range(len(column_labels)):
            if cell_text[i][j] < 0:
                cell_color[i][j] = "#c70200"
            else:
                cell_color[i][j] = "#01bb00"
            # print(cell_text[i][j] < 0)
            
    
    
    plt.figure(dpi=250)
    plt.table(cellText=cell_text, cellColours=cell_color, cellLoc='center', 
                             rowLabels=row_labels,colLabels=column_labels, colColours=None, 
                            colLoc='center', loc='center', edges='closed')
    plt.tick_params(axis='x', which='both', bottom=False, top=False, labelbottom=False)
    plt.tick_params(axis='y', which='both', right=False, left=False, labelleft=False)
    for pos in ['right','top','bottom','left']:
        plt.gca().spines[pos].set_visible(False)
    plt.tight_layout()
    plt.savefig('set2_1_4.png')
        
    
    # loc='bottom',
    # colWidths=None,
    # bbox=None,
    # rowLoc='left',
    
    
    
    
    
    
    
