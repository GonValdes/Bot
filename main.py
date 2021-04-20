import get_cash_flow as gcf
import constants as keys

from telegram.ext import *
import logging
#Updater class continuously fetches new updates from telegram and passes them on to the Dispatcher class
#When creating an Updater, it will create a dispatcher and link them with a queue
#Register handler of different types in the dispatcher-> sort updates fetched on updater according to registered handlers
updater = Updater(token=keys.API_KEY, use_context=True)
dispatcher = updater.dispatcher
# Once an update is handled, all further handlers are ignored.

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',level=logging.INFO)


def start(update, context):
    context.bot.send_message(chat_id=update.effective_chat.id, text="I'm a bot, please talk to me!")

def state(update,context):
    if update.message.text.upper() in gcf.ticker_list:
        ticker = update.message.text.upper()
        gcf.generate_cash_flow_figure(ticker)
        context.bot.send_photo(chat_id=update.effective_chat.id, photo=open('cash_flow.png', 'rb'))
    else:
        context.bot.send_message(chat_id=update.effective_chat.id, text='Ticker no está en la lista')



start_handler = CommandHandler('start',start)#text that starts it
state_handler = MessageHandler(Filters.text & (~Filters.command),state)

dispatcher.add_handler(start_handler)
dispatcher.add_handler(state_handler)

updater.start_polling()