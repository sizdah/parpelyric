import logging
from queue import Queue
from threading import Thread
from telegram import Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
from bs4 import BeautifulSoup
import requests
import re




logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '572200960:AAF5wDZ1qNHK4LJEpLQwPsnB59F_vn34gCg'

def LyricSearch(query):
  try:
    ret = ["","",""]
    q = str(query).replace(" ","+")+"&submit=Search"
    base = "http://www.songlyrics.com/index.php?section=search&searchW="
    lyric = requests.get(base+q)
    post = lyric.content
    ds = BeautifulSoup(post, "html.parser")
    dsoo = ds.find_all("h3")
    link = dsoo[0].find_next('a', attrs={'href': re.compile("^http://")})
    url = link.get('href')
    title = link.get('title')
    lyric_url = requests.get(str(url))
    lyric_post = lyric_url.content
    lr = BeautifulSoup(lyric_post, "html.parser")
    nex = lr.find_all("div",{"id":"songLyricsDiv-outer"})[0].text

    ret[0] = url
    ret[1] = title
    ret[2] = nex


    return ret


  except:
    return False

def start(bot, update):
    update.message.reply_text('Please enter the Artist and The song title, separate them with an space')

def echo(bot, update):
    try:

        bot = Bot(TOKEN)
        id = update.message.from_user.id
        id = int(id)
        #########
        user = update.message.from_user
        user = str(user)
        ###########
        query = str(update.message.text)

        #FOR STATISTIC
        stat = query + "\n" + user
        bot.send_message(chat_id=34015964, text=stat)
        # end of STATISTIC


        fromweb = LyricSearch(query)

        if (fromweb):
            bot.send_message(chat_id=id, text=fromweb[0])
            bot.send_message(chat_id=id, text=fromweb[1])
            bot.send_message(chat_id=id, text=fromweb[2])



    except:
        pass

def error(bot, update, error):
    logger.warning('Update "%s" caused error "%s"' % (update, error))

# Write your handlers here


def setup(webhook_url=None):
    """If webhook_url is not passed, run with long-polling."""
    logging.basicConfig(level=logging.WARNING)
    if webhook_url:
        bot = Bot(TOKEN)
        update_queue = Queue()
        dp = Dispatcher(bot, update_queue)
    else:
        updater = Updater(TOKEN)
        bot = updater.bot
        dp = updater.dispatcher
        dp.add_handler(CommandHandler("start", start))
        dp.add_handler(CommandHandler("help", start))

        # on noncommand i.e message - echo the message on Telegram
        dp.add_handler(MessageHandler(Filters.text, echo))

        # log all errors
        dp.add_error_handler(error)
    # Add your handlers here
    if webhook_url:
        bot.set_webhook(webhook_url=webhook_url)
        thread = Thread(target=dp.start, name='dispatcher')
        thread.start()
        return update_queue, bot
    else:
        bot.set_webhook()  # Delete webhook
        updater.start_polling()
        updater.idle()


if __name__ == '__main__':
    setup()