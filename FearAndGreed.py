# -*- coding: utf-8 -*-
"""
#https://github.com/hsauers5/FearAndGreed

"""


import requests
from bs4 import BeautifulSoup
import time
import datetime
import os
import pandas as pd

work_path = os.getcwd()

class IncrementableDate:
    def __init__(self, date_time=None, datestring=None, dateformat='%Y%m%d'):
        if date_time is not None:
            self.value = date_time

        elif datestring is not None:
            self.value = datetime.datetime.strptime(datestring,  dateformat)

    def to_string(self, dateformat='%Y%m%d'):
        return datetime.datetime.strftime(self.value, dateformat)

    def increment(self, offset=1):
        self.value += datetime.timedelta(days=offset)

    def __eq__(self, other):
        if isinstance(other, IncrementableDate):
            return self.value == other.value
        return NotImplemented

    def __ne__(self, other):
        x = self.__eq__(other)
        if x is not NotImplemented:
            return not x
        return NotImplemented

    def __gt__(self, other):
        if isinstance(other, IncrementableDate):
            return self.value > other.value
        return NotImplemented
    
    def __lt__(self, other):
        if isinstance(other, IncrementableDate):
            return self.value < other.value
        return NotImplemented

    def __ge__(self, other):
        return self.__gt__(other) or self.__eq__(other)

    def __le__(self, other):
        return self.__lt__(other) or self.__eq__(other)


class FearAndGreed:
    BASE_URL = 'https://archive.org/wayback/available?url=money.cnn.com/data/fear-and-greed/&timestamp={TIMESTAMP}'

    def get_historical_url(self, timestamp='20190101'):
        for i in range(0, 5):
            try:
                resp = requests.get(self.BASE_URL.replace('{TIMESTAMP}', timestamp)).json()
                hist_url = resp['archived_snapshots']['closest']['url']
            except KeyError:
                time.sleep(1)
            except:
                time.sleep(1)
        
        return hist_url

    def get_historical_score(self, historical_url=None, timestamp=None):
        if historical_url is None and timestamp is not None:
            historical_url = self.get_historical_url(timestamp)

        resp = requests.get(historical_url).content
        soup = BeautifulSoup(resp, 'html.parser')
        chart = soup.find('div', {'id': 'needleChart'})
        current_score = chart.find('li').text
        current_score = current_score.replace('Fear & Greed Now: ', '').split(' ')[0]

        return current_score

    
def run():
    scores_list = []
    date_list = []
    today_date = datetime.datetime.today().strftime('%Y%m%d')
    date_ago = (datetime.datetime.today() - datetime.timedelta(days = 365*10 )).strftime('%Y%m%d')
    begin_date = IncrementableDate(datestring=date_ago)
    end_date = IncrementableDate(datestring=today_date)
    datetime.date
    current_date = begin_date

    FG = FearAndGreed()

    while current_date <= end_date:
        try:
            score = FG.get_historical_score(timestamp=current_date.to_string())
        
            print(current_date.to_string() + ' ' + str(score))

            scores_list.append(score)
            date_list.append(current_date.to_string())

            current_date.increment(offset=7)
            
        except:
            current_date.increment(offset=7)
            pass

    with open('FGdata.txt', 'w+') as f:
        f.writelines(['Date'  + ' '+ 'FG' + '\n' ])
        f.writelines([str(date_list[i])  + ' '+ str(scores_list[i]) + '\n' for i in range(len(scores_list))])

def update():
    data = pd.read_csv(work_path+'\\'+'FGdata.txt', delimiter = " ")
    last_date = pd.to_datetime(data.iloc[-1,0],format='%Y%m%d')
    
    scores_list = []
    date_list = []
    today_date = datetime.datetime.today().strftime('%Y%m%d')
    date_ago = ( last_date - datetime.timedelta(days = -1 )).strftime('%Y%m%d')
    begin_date = IncrementableDate(datestring=date_ago)
    end_date = IncrementableDate(datestring=today_date)
    datetime.date
    current_date = begin_date

    FG = FearAndGreed()

    while current_date <= end_date:
        try:
            score = FG.get_historical_score(timestamp=current_date.to_string())
        
            print(current_date.to_string() + ' ' + str(score))

            scores_list.append(score)
            date_list.append(current_date.to_string())

            current_date.increment(offset=7)
            
        except:
            current_date.increment(offset=7)
            pass

    with open('FGdata.txt', 'w+') as f:
        f.writelines(['Date'  + ' '+ 'FG' + '\n' ])
        f.writelines([str(data.iloc[i,0])  + ' '+ str(data.iloc[i,1]) + '\n' for i in range(len(data))])
        f.writelines([str(date_list[i])  + ' '+ str(scores_list[i]) + '\n' for i in range(len(scores_list))])

#if __name__ == '__main__':
# update()
# run()