# -*- coding: utf-8 -*-
"""
Created on Sun May  2 16:22:17 2021

@author: gonza
"""

import os
work_path = 'C:\\Users\\gonza\\OneDrive\\Escritorio\\BOLSA\\Current'
os.chdir(work_path)
import macro_functions as mcf
import pandas as pd
import PDF_gen_macro as pdf_macro
import company_functions as cfun
import PDF_gen_company as pdf_comp
from urllib.request import urlopen
import json
import shutil

ticker= 'OKTA'
# Financialmodelingprep api url
base_url = "https://financialmodelingprep.com/api/v3/";
#personal key from https://financialmodelingprep.com/developer/docs/dashboard
apiKey = "df4be8c5528ea000a53c50e5a49850cf" ;

def get_macro(ticker):
    ## Macro economics
    mcf.get_macro_plots(mcf.time_ago(365*10), mcf.time_ago(0))
    pdf_macro.run_pdf()

def get_company(ticker):
    country = 'United States'
    cfun.get_company_data(ticker, country)
    pdf_comp.run_pdf_fund(ticker)
    pdf_comp.run_pdf_tech(ticker)
    os.replace(work_path+'\\company_images\\'+'{0}fund_report.pdf'.format(ticker), 
                work_path+'\\{0}fund_report.pdf'.format(ticker))
    os.replace(work_path+'\\company_images\\'+'{0}tech_report.pdf'.format(ticker), 
                work_path+'\\{0}tech_report.pdf'.format(ticker))
    [os.remove(file) for file in os.listdir(os.getcwd())]
    os.chdir(work_path)

def get_tickers_list():
    tickers = pd.DataFrame(get_jsonparsed_data(base_url +'available-traded/list?' + '&apikey=' + apiKey))
    tickers = tickers.values[:,0]
    return tickers

def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)


# os.chdir(work_path+'\\company_images')

ticker_list = get_tickers_list()
