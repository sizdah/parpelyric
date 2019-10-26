import logging
from queue import Queue
from threading import Thread
from telegram import Bot,ReplyKeyboardMarkup,ReplyKeyboardRemove
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, Updater, Filters
from bs4 import BeautifulSoup
import requests
import re,glob,os
from pytube import YouTube

lock = False
query_mem = ""

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)
TOKEN = '994506339:AAEe-V7J_K1n6bIwXtUu1BnAvhPXy6xgb5c'

def nope(bot,update):

    global query_mem

    if query_mem =="":
        return -1
    id = update.message.from_user.id
    id = int(id)
    reply_markup = ReplyKeyboardRemove()
    bot.send_message(chat_id=id, text="All right then", reply_markup=reply_markup)
    query_mem=""



def sure(bot,update):
    global lock
    global query_mem

    if query_mem == "":
        return -1

    try:
        li = glob.glob("*.mp4")
        for item in li:
            os.remove(str(item))
    except:
        pass


    lock = True
    id = update.message.from_user.id
    id = int(id)
    reply_markup = ReplyKeyboardRemove()
    bot.send_message(chat_id=id, text="Please hold on a little bit, Audio file will be sent to you in minutes as it gets ready...", reply_markup=reply_markup)
    file = download(query_mem)
    if file:
        try:
            bot.send_document(chat_id=id, document=open(str(file), 'rb'))
            os.remove(str(file))
        except:
           update.message.reply_text(" Download Failed ")
    query_mem=""
    lock = False

def download(link):
   try:
    link = str (link)
    yt = YouTube(link)
    stream = yt.streams.filter(only_audio=True).first()
    stream.download()
    namelist = (glob.glob("*.mp4"))
    return namelist[0]
   except:
       return False


def youtube(q):
   try:
    base = "https://www.youtube.com/results?search_query="
    qstring = str(q)+" song "
    qstring = qstring.replace(" ","+")

    r = requests.get(base + qstring)
    page = r.content
    soup = BeautifulSoup(page, 'html.parser')

    vids = soup.findAll('a', attrs={'class': 'yt-simple-endpoint'})
    v = vids[0]
    tmp = 'https://www.youtube.com' + v['href']
    tmp = str(tmp)
    return tmp
   except:
       return False


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
 global query_mem
 global lock

 if not lock:
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
            bot.send_message(chat_id=id, text=fromweb[1])
            bot.send_message(chat_id=id, text=fromweb[2])
        #    bot.send_message(chat_id=id, text=fromweb[0])
            vid = str (youtube(query))
            query_mem = vid
            bot.send_message(chat_id=id, text=vid)
     #       update.message.reply_text("Audio file will be sent to you in minutes as it gets ready")
            custom_keyboard = [
                ['/sure '],
                ['/nope']
            ]
            reply_markup = ReplyKeyboardMarkup(custom_keyboard)
            bot.send_message(chat_id=id, text="Would you like to download the music audio file?", reply_markup=reply_markup)



        else:
            update.message.reply_text("not found")



    except:
        pass
 else:
     update.message.reply_text("Server is busy, please try again later")

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
        dp.add_handler(CommandHandler("sure", sure))
        dp.add_handler(CommandHandler("nope", nope))

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
