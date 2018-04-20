import time
from pprint import pprint
import telepot
from telepot.loop import MessageLoop
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import json

with open("config.json") as config_data:
    config = json.load(config_data)
TOKEN = config['bot']['token']
CHANNEl = config['channel']['id']
bot = telepot.Bot(TOKEN)

def on_chat_message(msg):
    pprint(msg)
    content_type, chat_type, chat_id = telepot.glance(msg)
    auth = False
    if chat_id in config["user"]["users"]:
        auth = True
    if (not auth or content_type != 'voice') and chat_type=="private":
        bot.sendMessage(chat_id, "سرت سلامت باشه!")
    if auth and content_type and chat_type=="private" == 'voice':
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text='بره؟!', callback_data='press')],
               ])

        bot.sendMessage(chat_id, 'بره کانال؟!', reply_markup=keyboard, reply_to_message_id=msg['message_id'])

def on_callback_query(msg):
    query_id, from_id, query_data = telepot.glance(msg, flavor='callback_query')
    print('Callback Query:', query_id, from_id, query_data)
    pprint(msg)

    bot.sendVoice(CHANNEl, msg['message']['reply_to_message']['voice']['file_id'])
    bot.answerCallbackQuery(query_id, text='اقا مبارکه!')
MessageLoop(bot, {'chat': on_chat_message,
                  'callback_query': on_callback_query}).run_as_thread()

while 1:
    time.sleep(10)