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
parser.add_argument('token', help='token from BotFather')
parser.add_argument('--url', help='url to query',
                    default='https://status.bigeagle.me/')

arg = parser.parse_args()
last_place = None
who_care = set()


def locate():
    resq = requests.get(arg.url)

    # NOTE: force UTF-8 for Blink
    resq.encoding = 'UTF-8'
    page = resq.text
    soup = BeautifulSoup(page, 'html.parser')
    name = None
    for div in soup.body.div.div.div.find_all('div'):
        match = re.match("(.+)在(.+)吗？", div.h2.contents[0])
        name = match.group(1)
        if div.h1.contents[0] == "在呢！":
            place = match.group(2)
            return name, place
    else:
        return name, None


def whether_move(bot, job):
    name, place = locate()
    global last_place
    if place != last_place:
        if place is None and last_place is not None:
            text = '{}离开了{}。'.format(name, last_place)
        elif place is not None and last_place is None:
            text = '{}到了{}。'.format(name, place)
        else:
            text = '{}离开了{}并且瞬间到达了{}，快问他怎么做到的。'.format(name, last_place, place)
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
    _, place = locate()
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
