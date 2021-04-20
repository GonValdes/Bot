
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
# For parsing financial statements data from financialmodelingprep api
from urllib.request import urlopen
import json

# Financialmodelingprep api url
base_url = "https://financialmodelingprep.com/api/v3/";
#personal key from https://financialmodelingprep.com/developer/docs/dashboard
apiKey = "df4be8c5528ea000a53c50e5a49850cf" ;

def get_jsonparsed_data(url):
    response = urlopen(url)
    data = response.read().decode("utf-8")
    return json.loads(data)

def generate_cash_flow_figure(ticker):
    cash_flow_statement = pd.DataFrame(get_jsonparsed_data(base_url+'cash-flow-statement/' + ticker + '?apikey=' + apiKey));
    cash_flow_statement = cash_flow_statement.set_index('date');
#
    cash_flow_statement[['freeCashFlow']].iloc[::-1].iloc[-15:].plot(kind='bar', title=ticker + ' Cash Flows')
    plt.tight_layout()
    plt.savefig('cash_flow.png', bbox_inches='tight')

def get_tickers_list():
    tickers = pd.DataFrame(get_jsonparsed_data(base_url +'stock/list?' + '&apikey=' + apiKey))
    tickers = tickers.values[:,0]
    return tickers

ticker_list = get_tickers_list()

