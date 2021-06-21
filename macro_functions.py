# -*- coding: utf-8 -*-
"""
Created on Sun May  2 16:21:22 2021

@author: gonza
"""


####
import pandas as pd
import os
from datetime import datetime,  timedelta
import investpy
import matplotlib.pyplot as plt
from pandas_datareader.data import DataReader
import FearAndGreed as FaG

#### Modify
work_path = os.getcwd()


### Define functions
def time_ago(n_days):
    date_ago = (datetime.today() - timedelta(days = n_days )).strftime('%d/%m/%Y')
    return date_ago

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

def get_fearandgreed_historical(work_path):
    FaG.update()
    data = pd.read_csv(work_path+'\\'+'FGdata.txt', delimiter = " ")
    data['Date'] = pd.to_datetime(data['Date'],format='%Y%m%d')
    data.set_index('Date', inplace=True)
    return data
    
def get_macro_plots(from_date,today_date):
    #Obtain macroeconomic data and plots
    ##Yield curve 1,2,3,5,10,30 years
    yield_curve = get_yield_curve(time_ago(2), today_date)
    #10 Yield bond data
    yield_ten = get_bond_data(10, from_date, today_date).iloc[:,3]

    ##FED balance
    fed_total = get_fred_data('WALCL',from_date)#total assets
    fed_rep = get_fred_data('WORAL',from_date)#assets:repurchases
    fed_ts = get_fred_data('WALCL',from_date)#tresury securities

    ##Money supply
    money_supply = get_fred_data('M2SL',from_date)

    #Inflation: Consumer Price Index, Producer Price Index and Inflation estimation from 5y bond
    PPI = get_fred_data('PPIACO',from_date) #real inflation. Selling prices received by producers
    CPI = get_fred_data('CPILFESL',from_date) # measure price of services and goods consumed by population
    inflation_est = get_fred_data('T5YIE',from_date)# expected inflation derived from 5-Year Treasury Constant Maturity Securities (BC_5YEAR) and 5-Year Treasury Inflation-Indexed Constant Maturity Securities (TC_5YEAR)
    
    #♣Unemployment
    unemp_USA = get_fred_data('UNRATE',from_date) 
    # unemp_EUR = get_fred_data('LRHUTTTTEZM156S',from_date) 
    
    #GDP
    GDP = get_fred_data('GDP',from_date)
    #GDP_real = get_fred_data('GDPC1',from_date)#'inflation adjusted'
    GDP_real_percap = get_fred_data('A939RX0Q048SBEA',from_date)#'inflation adjusted'per capita
    #Debt
    debt = get_fred_data('GFDEBTN',from_date)
    debt = debt/(10**3) 
    #Debt_GDP
    debt_GDP = get_fred_data('GFDEGDQ188S',from_date)

    #VIX
    VIX = get_fred_data('VIXCLS',from_date)
    #Fear and greed
    FG = get_fearandgreed_historical(work_path)
    FG = FG.loc[FG.index > from_date]
    #SP500
    SP = get_index_data('S&P 500','United States',from_date,today_date).iloc[:,3]
    
    ### Plot macros
    os.chdir(work_path+'\\macro_images')

    figure_size = [9,4.8]
    

    # GDP-DEBT
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(GDP,color='k',label='GDP')
    plt.plot(debt,color='b',label='Debt')
    plt.ylabel('billion $')
    plt.legend()
    plt.title('GDP and Debt')
    plt.grid()
    plt.savefig('set_1_1.png')

    plt.figure(figsize=figure_size,dpi=250)
    fig, ax1 = plt.subplots()
    color = 'k'#'tab:red'
    # ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Inflation adjusted GDP per capita($)', color=color)
    ax1.plot(GDP_real_percap, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Debt/GDP(%)', color=color)  # we already handled the x-label with ax1
    ax2.plot(debt_GDP, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.grid()
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('set_1_2.png')
    
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(unemp_USA,color='k',label='USA')
    plt.ylabel('Unemployment %')
    plt.legend()
    plt.grid()
    plt.title('Unemployment')
    plt.savefig('set_1_3.png')
    
    #INFLATION

    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(inflation_est ,color='k',label='USA')
    plt.ylabel('Inflation estimation %')
    plt.title('Expected yearly inflation derived from 5y yield')
    plt.legend()
    plt.grid()
    plt.savefig('set_2_1.png')
    
    plt.figure(figsize=figure_size,dpi=250)
    fig, ax1 = plt.subplots()
    color = 'k'#'tab:red'
    # ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Consumer Price Index', color=color)
    ax1.plot(CPI, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Producer Price Index', color=color)  # we already handled the x-label with ax1
    ax2.plot(PPI, color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.grid()
    plt.title('Inflation indices')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('set_2_2.png')
    
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(money_supply  ,color='k',label='USA')
    plt.ylabel('billion $')
    plt.title('Money supply')
    plt.grid()
    plt.savefig('set_2_3.png')
    
    
    #YIELD
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(yield_ten ,color='k')
    plt.ylabel('Yield(%)')
    plt.title('10y treasury yield')
    plt.grid()
    plt.savefig('set_3_1.png')
    
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(['1y','2y','3y','5y','10y','30y'],yield_curve ,color='k',label='USA')
    plt.ylabel('Yield(%)')
    plt.title('Yield curve')
    plt.grid()
    plt.savefig('set_3_2.png')
    
    #FED BALANCE
    
    plt.figure(figsize=figure_size,dpi=150)
    plt.plot(fed_total/(10**3) ,color='k')
    plt.ylabel('b$')
    plt.title('FED Balance')
    plt.grid()
    plt.savefig('set_4_1.png')
    
    plt.figure(figsize=figure_size,dpi=250)
    fig, ax1 = plt.subplots()
    color = 'k'#'tab:red'
    # ax1.set_xlabel('time (s)')
    ax1.set_ylabel('Assets repurchases (b$)', color=color)
    ax1.plot(fed_rep/(10**3), color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('Treasury securities(b$)', color=color)  # we already handled the x-label with ax1
    ax2.plot(fed_ts/(10**3), color=color)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.grid()
    plt.title('FED Balance insight')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('set_4_2.png')
    

    # VOLATILITY
    plt.figure(figsize=figure_size,dpi=250)
    fig, ax1 = plt.subplots()
    color = 'k'
    # ax1.set_xlabel('time (s)')
    ax1.set_ylabel('VIX', color=color)
    ax1.plot(VIX, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.grid()
    plt.ylim([0,100])
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('S&P 500', color=color)  # we already handled the x-label with ax1
    ax2.plot(SP, color=color, linewidth = 0.7)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title('VIX vs S&P 500')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('set_5_1.png')

    plt.figure(figsize=figure_size,dpi=250)
    fig, ax1 = plt.subplots()
    color = 'k'
    # ax1.set_xlabel('time (s)')
    ax1.set_ylabel('F&G', color=color)
    ax1.plot(FG, color=color)
    ax1.tick_params(axis='y', labelcolor=color)
    plt.grid()
    plt.ylim([0,100])
    ax2 = ax1.twinx()  # instantiate a second axes that shares the same x-axis
    color = 'tab:blue'
    ax2.set_ylabel('S&P 500', color=color)  # we already handled the x-label with ax1
    ax2.plot(SP, color=color, linewidth = 0.7)
    ax2.tick_params(axis='y', labelcolor=color)
    plt.title('Fear&Greed vs S&P 500')
    fig.tight_layout()  # otherwise the right y-label is slightly clipped
    plt.savefig('set_5_2.png')
    

# def generate_pdf():
#     pdf_gen.run_pdf()

    # Delete files 
    # dir = os.getcwd()
    # for f in os.listdir(dir):
    #     if f =='macro_report.pdf':
    #             os.remove(os.path.join(dir, f))
    #             try:
    #                 aux = f.replace('.','_').split('_')
    #                 if aux[3]=='png':
    #                     os.remove(os.path.join(dir, f))
    #             except:
    #                 continue
    
    # os.chdir(os.path.dirname(os.getcwd()))