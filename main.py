from telegram import (ReplyKeyboardMarkup, ReplyKeyboardRemove)
from telegram.ext import (Updater, CommandHandler, MessageHandler, Filters, RegexHandler,
                          ConversationHandler)
import logging
import json
from pprint import pprint
from pydub import AudioSegment
from functools import wraps
import os

with open("config.json") as config_data:
    config = json.load(config_data)
TOKEN = config['bot']['token']
CHANNEL = config['channel']['id']

LIST_OF_ADMINS = config['user']['users']

def restricted(func):
    @wraps(func)
    def wrapped(bot, update, *args, **kwargs):
        user_id = update.effective_user.id
        if user_id not in LIST_OF_ADMINS:
            print("Unauthorized access denied for {}.".format(user_id))
            return
        return func(bot, update, *args, **kwargs)
    return wrapped

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)

logger = logging.getLogger(__name__)

GETING_POST, GETING_AUDIO, TRIMING = range(3)

reply_keyboard = [['بفرست کانال']]
markup = ReplyKeyboardMarkup(reply_keyboard)
no_markup = ReplyKeyboardRemove()


@restricted
def start(bot, update):
    
    update.message.reply_text(
        "پست رو بفرست.", reply_markup = no_markup)

    return GETING_POST



def received_post(bot, update, user_data):
    post = update.message
    user_data['post'] = post
    # print(post)
    update.message.reply_text("حالا موزیک رو بفرست.",reply_markup = no_markup) 
    return GETING_AUDIO
def received_audio(bot, update, user_data):
    audio = update.message.audio
    user_data['audio'] = audio
    file_id = audio.file_id
    newFile = bot.get_file(file_id)
    newFile.download(file_id+".mp3")
    # print(audio)

    update.message.reply_text("حالا بگو از کجا برات ببرم؟", reply_markup = no_markup) 

    return TRIMING
def received_start_point(bot, update, user_data):
    start_point = int(update.message.text)
    if int(user_data['audio']['duration']) > 60 + start_point:
        user_data['start_point'] = start_point
    else:
        user_data['start_point'] = 0 

    print(update)
    update.message.reply_text("حالا میتونی بفرستی کانال", reply_markup=markup)

    return GETING_POST


def done(bot, update, user_data):
    if "start_point" not in user_data.keys():
        update.message.reply_text("از اول شروع کن")
        user_data.clear()
        return ConversationHandler.END

    start_point = user_data['start_point']
    post = user_data['post']
    audio = user_data['audio']
    file_id = audio.file_id
    song = AudioSegment.from_mp3(file_id + ".mp3")
    sliceAudio = song[start_point*1000:(start_point+30)*1000]
    sliceAudio.export(file_id +".ogg", format="mp3")
    
    bot.send_photo(chat_id = CHANNEL, photo=post['photo'][-1], caption = post['caption'])
    bot.send_audio(chat_id = CHANNEL, audio=audio, caption = CHANNEL)
    bot.send_voice(chat_id = CHANNEL, voice=open(file_id + '.ogg', 'rb'))

    update.message.reply_text("رفت رو کانال!")

    user_data.clear()
    os.remove(file_id+".mp3")
    os.remove(file_id+".ogg")

    
    return ConversationHandler.END


def error(bot, update, error):
    """Log Errors caused by Updates."""
    logger.warning('Update "%s" caused error "%s"', update, error)


def main():
    # Create the Updater and pass it your bot's token.
    updater = Updater(TOKEN)

    # Get the dispatcher to register handlers
    dp = updater.dispatcher

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[CommandHandler('newpost', start)],

        states = {
            GETING_POST: [MessageHandler(Filters.photo,
                                    received_post,
                                    pass_user_data=True),

                    ],
            GETING_AUDIO: [MessageHandler(Filters.audio,
                                    received_audio,
                                    pass_user_data=True),

                    ],
            TRIMING: [MessageHandler(Filters.text,
                                    received_start_point,
                                    pass_user_data=True)
                    ],
        },

        fallbacks = [RegexHandler('^بفرست کانال$', done, pass_user_data = True)]
    )

    dp.add_handler(conv_handler)

    # log all errors
    dp.add_error_handler(error)

    # Start the Bot
    updater.start_polling()

    # Run the bot until you press Ctrl-C or the process receives SIGINT,
    # SIGTERM or SIGABRT. This should be used most of the time, since
    # start_polling() is non-blocking and will stop the bot gracefully.
    updater.idle()


if __name__ == '__main__':
    main()