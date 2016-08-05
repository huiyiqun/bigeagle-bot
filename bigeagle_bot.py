import re
import requests
import logging
from argparse import ArgumentParser
from bs4 import BeautifulSoup
from telegram.ext import Updater, CommandHandler, Job

logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

parser = ArgumentParser(description='A bot to locate Bigeagle')
parser.add_argument('token', help='Token from BotFather')

arg = parser.parse_args()
last_place = None
who_care = set()


def locate():
    page = requests.get('https://status.bigeagle.me/').text
    soup = BeautifulSoup(page, 'html.parser')
    for div in soup.body.div.div.div.find_all('div'):
        if div.h1.contents[0] == "在呢！":
            place = re.match("团长在(.+)吗？", div.h2.contents[0]).group(1)
            return place


def whether_move(bot, job):
    place = locate()
    global last_place
    if place != last_place:
        if place is None and last_place is not None:
            text = '大鹰离开了{}。'.format(last_place)
        elif place is not None and last_place is None:
            text = '大鹰到了{}。'.format(place)
        else:
            text = '大鹰离开了{}并且瞬间到达了{}，快问他怎么做到的。'.format(last_place, place)
        while True:
            try:
                caring = who_care.pop()
            except KeyError:
                break
            bot.sendMessage(caring, text=text)
        last_place = place


def care(bot, update):
    who_care.add(update.message.chat_id)
    bot.sendMessage(update.message.chat_id, text='谢谢关心。')


def start(bot, update):
    bot.sendMessage(update.message.chat_id, text='Hello World!')


def where(bot, update):
    place = locate()
    if place is not None:
        bot.sendMessage(update.message.chat_id,
                        text="在{}呢。".format(place))
    else:
        # TODO: Random funny result
        bot.sendMessage(update.message.chat_id,
                        text="不知道哎。。。")

updater = Updater(arg.token)

updater.dispatcher.add_handler(CommandHandler('start', start))
updater.dispatcher.add_handler(CommandHandler('where', where))
updater.dispatcher.add_handler(CommandHandler('care', care))
query_task = Job(whether_move, 60.0)
updater.job_queue.put(query_task, next_t=0.0)

updater.start_polling()
updater.idle()
