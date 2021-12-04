import os
import qrcode
import random
import logging
from gtts import gTTS
from PIL import Image, ImageDraw
from khayyam import JalaliDate, JalaliDatetime
from telegram import (
    Update,
    ReplyKeyboardMarkup,
    InlineKeyboardMarkup,
    InlineKeyboardButton)
from telegram.ext import (
    Updater,
    Filters,
    MessageHandler,
    CommandHandler,
    CallbackContext,
    ConversationHandler,
    CallbackQueryHandler)

BASE, GET_BORN_DATE, GET_EN_TEXT, MAX_ARRAY, MAX_ARRAY_INDEX, GET_QR_TEXT, GUESS = range(7)
randn = int(random.random() * 100)

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
                    level=logging.INFO)
logger = logging.getLogger(__name__)


def error(update, context):
    logger.warning('Update "%s" caused error "%s"', update, context.error)


def kb_error(update: Update, _: CallbackContext):
    update.message.reply_text(text='لطفا از لیست دستورات استفاده کنید!')


def start(update: Update, _: CallbackContext):
    update.message.reply_text(text='سلام ' + update.effective_user.first_name + ' خوش آمدی!')
    return BASE


def game(update: Update, _: CallbackContext):
    update.message.reply_text(text='بازی حدس عدد!'
                                   '\nتو این بازی یه عدد بین 10 و 100 حدس میزنی '
                                   'و من راهنماییت میکنم تا به عدد اصلی برسی.'
                                   '\n\nاولین حدست چیه؟',
                              reply_markup=ReplyKeyboardMarkup(
                                  keyboard=[['بازی جدید']],
                                  resize_keyboard=True,
                                  one_time_keyboard=True))
    return GUESS


def new_randn():
    global randn
    randn = int(random.random() * 100)


def guess(update: Update, _: CallbackContext):
    if update.message.text == 'بازی جدید':
        new_randn()
        update.message.reply_text(text='خب دوباره بگو...\n\nاولین حدست چیه؟',
                                  reply_markup=ReplyKeyboardMarkup(
                                      keyboard=[['بازی جدید']],
                                      resize_keyboard=True,
                                      one_time_keyboard=True))
        return GUESS
    elif int(update.message.text) < randn:
        update.message.reply_text(text='حدست کمتره برو بالا')
    elif int(update.message.text) > randn:
        update.message.reply_text(text='حدست بیشتره بیا پایین')
    elif int(update.message.text) == randn:
        update.message.reply_text(text='آفرین درست حدس زدی!\nعدد مورد نظر: ' + str(randn))
        new_randn()
    else:
        update.message.reply_text(text='داری اشتباه میزنی!')


def age(update: Update, _: CallbackContext):
    update.message.reply_text(text='دوست عزیر تاریخ تولدت رو به صورت زیر برام بفرس.\n\nمثال: 1400 12 12')
    return GET_BORN_DATE


def send_age(update: Update, _: CallbackContext):
    if len(update.message.text.split()) == 3:
        year = int(update.message.text.split()[0])
        month = int(update.message.text.split()[1])
        day = int(update.message.text.split()[2])
        age = str(JalaliDatetime.now() - JalaliDate(year, month, day)).split()[0]
        age_Y = int(age) // 365
        age_M = (int(age) - (365 * age_Y)) // 30
        age_D = int(age) - age_Y * 365 - age_M * 30
        update.message.reply_text(text='سن شما:\n\n' +
                                       str(age_Y) + ' سال و ' +
                                       str(age_M) + ' ماه و ' +
                                       str(age_D) + ' روز ')

    else:
        update.message.reply_text(text='فرمت نادرست\nتاریخ تولدت رو دوباره به صورت زیر برام بفرس.\n\nمثال: 1400 12 12')
        return GET_BORN_DATE


def voice(update: Update, _: CallbackContext):
    update.message.reply_text(text='متن مورد نظر خود را برای تبدیل به ویس بفرستید.\nمتن باید انگلیسی باشد')
    return GET_EN_TEXT


def send_voice(update: Update, _: CallbackContext):
    text = update.message.text
    voice = gTTS(text=text, lang='en', slow=False)
    voice.save('text2voice.ogg')
    voice = open('text2voice.ogg', 'rb')
    update.message.reply_voice(voice=voice)


def maxn(update: Update, _: CallbackContext):
    update.message.reply_text(text='آرایه های عددی به صورت زیر وارد کید تا بیشترین مقدار چاپ شود\n\n'
                                   '15 7 8 12 9 10')
    return MAX_ARRAY


def send_max(update: Update, _: CallbackContext):
    list = update.message.text.split()
    a = []
    for number in list:
        a.append(int(number))
    maximum = max(a)
    update.message.reply_text(text='بزرگترین عدد: ' + str(maximum))


def maxn_index(update: Update, _: CallbackContext):
    update.message.reply_text(text='آرایه های عددی به صورت زیر وارد کید تا شماره ردیف بزرگ ترین عدد چاپ شود\n\n'
                                   '15 7 8 12 9 10')
    return MAX_ARRAY_INDEX


def send_max_index(update: Update, _: CallbackContext):
    list = update.message.text.split()
    a = []
    for number in list:
        a.append(int(number))
    maximum = max(a)
    index = a.index(maximum)
    update.message.reply_text(text='ردیف بزرگترین عدد: ' + str(index + 1))


def qr_code(update: Update, _: CallbackContext):
    update.message.reply_text(text='متن مورد نظر خود را برای تبدیل به QR_code بفرستید.')
    return GET_QR_TEXT


def send_qrcode(update: Update, _: CallbackContext):
    text = update.message.text
    img = qrcode.make(text)
    img.save('qrcode.png')
    img = open('qrcode.png', 'rb')
    update.message.reply_photo(photo=img)


def help(update: Update, _: CallbackContext):
    update.message.reply_text(text='<b>دستور های ربات</b>:\n\n/start : شروع مجدد'
                                   '\n/game : بازی حدس عدد'
                                   '\n/age : محاسبه سن'
                                   '\n/voice : تبدیل متن به صدا'
                                   '\n/max : بیشترین مقدار یک آرایه عددی'
                                   '\n/argmax :  ردیف بیشترین مقدار یک آرایه عددی'
                                   '\n/qrcode : تبدیل متن به کیو آر کد',
                              parse_mode='HTML')


def main():
    TOKEN = os.environ['TOKEN']
    updater = Updater(TOKEN)
    conv_handler0 = ConversationHandler(
        entry_points=[CommandHandler('start', start),
                      CommandHandler('game', game),
                      CommandHandler('age', age),
                      CommandHandler('voice', voice),
                      CommandHandler('max', maxn),
                      CommandHandler('argmax', maxn_index),
                      CommandHandler('qrcode', qr_code),
                      CommandHandler('help', help)],
        states={
            BASE: [MessageHandler(Filters.text & ~Filters.command, kb_error),
                   CommandHandler('start', start),
                   CommandHandler('game', game),
                   CommandHandler('age', age),
                   CommandHandler('voice', voice),
                   CommandHandler('max', maxn),
                   CommandHandler('argmax', maxn_index),
                   CommandHandler('qrcode', qr_code),
                   CommandHandler('help', help)],
            GET_BORN_DATE:
                [MessageHandler(Filters.regex('[0-9]') & ~Filters.command, send_age),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)],
            GET_EN_TEXT:
                [MessageHandler(Filters.text & ~Filters.command, send_voice),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)],
            MAX_ARRAY:
                [MessageHandler(Filters.regex('[0-9]') & ~Filters.command, send_max),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)],
            MAX_ARRAY_INDEX:
                [MessageHandler(Filters.regex('[0-9]') & ~Filters.command, send_max_index),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)],
            GET_QR_TEXT:
                [MessageHandler(Filters.text & ~Filters.command, send_qrcode),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)],
            GUESS:
                [MessageHandler(Filters.text & ~Filters.command, guess),
                 CommandHandler('start', start),
                 CommandHandler('game', game),
                 CommandHandler('age', age),
                 CommandHandler('voice', voice),
                 CommandHandler('max', maxn),
                 CommandHandler('argmax', maxn_index),
                 CommandHandler('qrcode', qr_code),
                 CommandHandler('help', help)]
        },
        fallbacks=[CommandHandler('help', help)])

    conv_handler1 = CommandHandler('start', start)
    conv_handler2 = CommandHandler('game', game)
    conv_handler3 = CommandHandler('age', age)
    conv_handler4 = CommandHandler('voice', voice)
    conv_handler5 = CommandHandler('max', maxn)
    conv_handler6 = CommandHandler('argmax', maxn_index)
    conv_handler7 = CommandHandler('qrcode', qr_code)
    conv_handler8 = CommandHandler('help', help)
    updater.dispatcher.add_handler(conv_handler0)
    updater.dispatcher.add_handler(conv_handler1)
    updater.dispatcher.add_handler(conv_handler2)
    updater.dispatcher.add_handler(conv_handler3)
    updater.dispatcher.add_handler(conv_handler4)
    updater.dispatcher.add_handler(conv_handler5)
    updater.dispatcher.add_handler(conv_handler6)
    updater.dispatcher.add_handler(conv_handler7)
    updater.dispatcher.add_handler(conv_handler8)


    updater.start_polling()
    updater.idle()


if __name__ == '__main__':
    main()
