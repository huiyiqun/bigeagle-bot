import re
import requests
import logging
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

parser = ArgumentParser(description='A bot to locate Bigeagle')
parser.add_argument('token', help='Token from BotFather')

arg = parser.parse_args()

def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello World!')

def where(bot, update):
    page = requests.get('https://status.bigeagle.me/').text
    soup = BeautifulSoup(page, 'html.parser')
    for div in soup.body.div.div.div.find_all('div'):
        if div.h1.contents[0] == "在呢！":
            place = re.match("团长在(.+)吗？", div.h2.contents[0]).group(1)
            bot.sendMessage(update.message.chat_id,
                            text="在{}呢。".format(place))
            return
    else:
        # TODO: Random funny result
        bot.sendMessage(update.message.chat_id,
                        text="不知道哎。。。")

updater = Updater(arg.token)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('where', where))

updater.start_polling()
updater.idle()
