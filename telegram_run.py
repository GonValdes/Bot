"""
Created on Apr 2021

@author: Gonzalo Valdés
mail:gonzalovaldescernuda@gmail.com

Script to run the telegram bot based on python-telegram-bot package.
Input a ticker to obtain a report with fundamental and technical data
"""
import os
work_path = 'C:\\Users\\gonza\\OneDrive\\Escritorio\\BOLSA\\Current'
os.chdir(work_path)
import run_scripts as run_scripts
import constants as keys
from telegram.ext import *
import logging

#

#Updater class continuously fetches new updates from telegram and passes them on to the Dispatcher class
#When creating an Updater, it will create a dispatcher and link them with a queue
#Register handler of different types in the dispatcher-> sort updates fetched on updater according to registered handlers
updater = Updater(token=keys.API_KEY, use_context=True)
dispatcher = updater.dispatcher
# Once an update is handled, all further handlers are ignored.

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, 
                             text='State the company to analyse')

def state(update,context):
    #Check if the ticker is in the stock list
    if update.message.text.upper() in run_scripts.ticker_list:
        #Run the script to obtain the reports
        ticker = update.message.text.upper()
        run_scripts.get_company(ticker)
        #Send the reports
        context.bot.send_document(chat_id=update.effective_chat.id,document = open('{0}fund_report.pdf'.format(ticker), 'rb'))
        context.bot.send_document(chat_id=update.effective_chat.id,
                                  document=open('{0}tech_report.pdf'.format(ticker), 'rb'))
        #Delete the report files
        os.remove('{0}fund_report.pdf'.format(ticker))
        os.remove('{0}tech_report.pdf'.format(ticker))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, 
                                 text='Ticker not in list. Only US companies can be analysed for the moment')

start_handler = CommandHandler('start',start)#text that starts it
state_handler = MessageHandler(Filters.text & (~Filters.command),state)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(state_handler)

updater.start_polling()