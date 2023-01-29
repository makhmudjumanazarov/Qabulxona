from telegram.ext import Updater, CommandHandler, MessageHandler, CallbackQueryHandler
from telegram import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext.filters import Filters

from nemo.collections import nlp as nemo_nlp
from nemo.utils.exp_manager import exp_manager
from clean_data import toza
import sqlite3
import pandas as pd

# load model
checkpoint_path = '/home/airi/Desktop/jupyter/til model/text classification/nemo_experiments/TextClassification/2023-01-28_22-27-15/checkpoints/TextClassification--val_loss=1.5892-epoch=9.ckpt'
infer_model = nemo_nlp.models.TextClassificationModel.load_from_checkpoint(checkpoint_path=checkpoint_path)
infer_model.to("cuda")

classes = ["Aloqa va kommunikatsiya","Pul munosabatlari","Ekologiya","Sanitariya",\
           "Din va Millat","Transport","Oila","Ta'lim va madaniyat","Hech qaysiga kirmaydi"]

# import logging
# logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.DEBUG)

# bazaga ulanish
mydb = sqlite3.connect("murojaat.db", check_same_thread=False)

global cursor
cursor = mydb.cursor()

def password():
    characters = list(string.ascii_letters + string.digits + "!@#$%^&*()")
    ## shuffling the characters
    random.shuffle(characters)
	
    ## picking random characters from the list
    password = []
    for i in range(16):
        password.append(random.choice(characters))

    ## shuffling the resultant password
    random.shuffle(password)

    ## converting the list to string
    ## printing the list
    return "".join(password)


cursor.execute("DROP TABLE users")
cursor.execute("CREATE TABLE users (ism varchar(30), fam varchar(30), sharif varchar(30), hudud varchar(15), manzil varchar(100), tug_sana varchar(10), chat_id varchar(10), status int)")
mydb.commit()

cursor.execute("DROP TABLE murojaat")
cursor.execute("CREATE TABLE murojaat (chat_id varchar(10), message_id varchar(10), matn varchar(2048), committee varchar(100))")
mydb.commit()

cursor.execute(f'SELECT * FROM users')
a = cursor.fetchall()
for i in range(len(a)):
    print(a[i])
    

global regions, groups
groups = [-888208875,-832264981,-845084236,-812979406,-860698397,-846297376,-877732417,-670846743]
regions = ['Qashqadaryo','Toshkent shahri','Toshkent viloyati','Andijon','Farg\'ona','Namangan','Jizzax',\
           'Sirdaryo','Samarqand','Surxondaryo','Navoiy','Buxoro','Xorazm','Qoraqalpog\'iston Respublikasi']


def start(update, context):
    chat_id = update.message.chat.id
    cursor.execute(f'SELECT COUNT(*) FROM users WHERE chat_id=?', (str(chat_id),))
    user = cursor.fetchall()
    if user[0][0]==0:
        query = f'INSERT INTO users (ism,fam,sharif,hudud,manzil,tug_sana,chat_id,status) VALUES(?,?,?,?,?,?,?,1)'
        cursor.execute(query, (None,None,None,None,None,None,str(chat_id)))
        log_in(update, context, chat_id)
    else:
        keyboard = [[KeyboardButton(text = 'Yangi murojaatnoma')]]
        update.message.reply_text(
            text='Assalomu alaykum, xalq murojaatlarini qabul qiluvchi botga xush kelibsiz!',
            reply_markup=ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True
                )
            )
    
def log_in(update, context, chat_id):
    context.bot.send_message(
        chat_id=chat_id,
        text='Assalomu alaykum, xalq murojaatlarini qabul qiluvchi botga xush kelibsiz!\nBotdan foydalanish uchun quyidagi ma\'lumotlarni kiriting:',
        )
    ism(update, context, chat_id)
    
def ism(update, context, chat_id):
    context.bot.send_message(
        chat_id=chat_id,
        text='Ismingiz:',
        )

def fam(update, context, chat_id):
    context.bot.send_message(
        chat_id=chat_id,
        text='Familiyangiz:',
        )

def sharif(update, context, chat_id):
    context.bot.send_message(
        chat_id=chat_id,
        text='Sharifingiz:',
        )
    
def hudud(update, context, chat_id):
    global regions
    context.bot.send_message(
        chat_id=chat_id,
        text='Hududingiz:',
        reply_markup=InlineKeyboardMarkup(inline_keyboard = [[InlineKeyboardButton(regions[2*i+j], callback_data=f'vil{2*i+j}') for j in range(2)] for i in range(7)]),
        )

def manzil(update, context,chat_id):
    context.bot.send_message(
        text='Manzilingiz(tuman, ko\'cha, uy):',
        chat_id=chat_id
        )

def tug_sana(update, context,chat_id):
    context.bot.send_message(
        text='Tug\'ilgan kuningizni kiriting(format: kk.oo.yyyy):',
        chat_id=chat_id
        )
    
def commands(update, context):
    global groups
    chat_id = update.message.chat.id
    print(type(chat_id))
    text = update.message.text

def buyruq(update, context):
    global groups
    chat_id = update.message.chat.id
    text = update.message.text
    cursor.execute(f"SELECT * FROM users")
    cols = list(map(lambda x: x[0], cursor.description))                             # shuni tahrirlash kerak
    # print(text)
    # print(update.message,end='\n\n')
    if text == 'Yangi murojaatnoma':
        update.message.reply_text(
            text='Murojaatnomangizni yo\'llang:'
        )
    else:
        # for users
        cursor.execute(f'SELECT COUNT(*) FROM users WHERE chat_id=? and status=1', (str(chat_id),))
        user = cursor.fetchall()
        if user[0][0]==1:
            cursor.execute(f'SELECT * FROM users WHERE chat_id=?', (str(chat_id),))
            inp = cursor.fetchall()[0][:6]
            ind = inp.index(None)
            query = f"UPDATE users SET {cols[ind]}=? WHERE chat_id=?"
            cursor.execute(query, (text,chat_id))
            mydb.commit()
            if ind == 0:
                fam(update,context,chat_id)
            elif ind == 1:
                sharif(update,context,chat_id)
            elif ind == 2:
                hudud(update,context,chat_id)
            elif ind == 3:
                manzil(update,context,chat_id)
            elif ind == 4:
                tug_sana(update,context,chat_id)
            else:
                cursor.execute(f"UPDATE users SET status=0 WHERE chat_id={chat_id}")
                mydb.commit()
                keyboard = [[KeyboardButton(text = 'Yangi murojaatnoma')]]
                update.message.reply_text(
                    text='Murojaatnomangizni yo\'llang:',
                    reply_markup=ReplyKeyboardMarkup(
                        keyboard=keyboard,
                        resize_keyboard=True
                        )
                    )
        else:
            if update.message.chat.type == 'group':
                if type(update.message.reply_to_message) != type(None):
                    reply_mid = update.message.reply_to_message.message_id
                    cursor.execute(f"SELECT chat_id FROM murojaat WHERE message_id={reply_mid}")
                    user_chatid = list(cursor.fetchall()[0])[0]
                    context.bot.send_message(
                        chat_id=user_chatid,
                        text=text
                    )
                    context.bot.send_message(
                        chat_id=user_chatid,
                        text='Javobdan qoniqdingizmi?',
                        reply_markup=InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton('Ha✅', callback_data='1'),InlineKeyboardButton('Yo\'q❌', callback_data='0')]])
                    )
            else:
                committee = groups[text_class(text)]
                murojaat = context.bot.send_message(
                    text=text,
                    chat_id=committee
                )
                query = f"INSERT INTO murojaat(chat_id, message_id, matn, committee) VALUES(?,?,?,?)"
                cursor.execute(query, (chat_id,murojaat.message_id,text,committee))
                mydb.commit()

                
# function for text classification
def text_class(text):
    query = list(toza.transform(pd.DataFrame({'content':[text]}))['content'])
    results = infer_model.classifytext(queries=query, batch_size=3, max_seq_length=512)
    return results[0]


def query_handler(update, context):
    global regions
    chat_id = update.callback_query.message.chat.id
    query = update.callback_query.data
    if not query.isdigit():
        surov = f"UPDATE users SET hudud=? WHERE chat_id=?"
        if query[len(query)-2:].isdigit():
            ind_reg = int(query[len(query)-2:])
        else:
            ind_reg = int(query[-1])
        cursor.execute(surov, (regions[int(ind_reg)],chat_id))
        mydb.commit()

        cursor.execute(f'SELECT * FROM users WHERE chat_id=?', (str(chat_id),))
        inp = cursor.fetchall()[0][:6]
        ind = inp.index(None)
        if ind == 4:
            manzil(update,context,chat_id)
    else:
        if query == '1':
            keyboard = [[KeyboardButton(text = 'Yangi murojaatnoma')]]
            context.bot.send_message(
                chat_id=chat_id,
                text='🎉🎉🎉Sizga yordam berganimdan xursandman!!!🎉🎉🎉',
                reply_markup=ReplyKeyboardMarkup(
                    keyboard=keyboard,
                    resize_keyboard=True
                    )
                )
        elif query == '0':
            surov = f"SELECT matn,committee FROM murojaat WHERE chat_id=?"
            cursor.execute(surov, (chat_id,))
            javob = list(cursor.fetchall()[-1])
            matn, group_id = javob[0], javob[1]
            murojaat = context.bot.send_message(
                text=matn,
                chat_id=group_id
            )
            query = f"INSERT INTO murojaat(chat_id, message_id, matn, committee) VALUES(?,?,?,?)"
            cursor.execute(query, (chat_id,murojaat.message_id,matn,group_id))
            mydb.commit()
            context.bot.send_message(
                chat_id=chat_id,
                text='Murojaatingiz ko\'rib chiqish uchun qayta jo\'natildi!'
                )
            


updater = Updater(token = '5416793968:AAFpctohXhujf1dy2QN8gUzCvUWz-xa8v64')
dispatcher = updater.dispatcher

dispatcher.add_handler(CommandHandler('Start', start))
dispatcher.add_handler(CommandHandler('Restart', start))
# dispatcher.add_handler(MessageHandler(Filters.document, get_py))
dispatcher.add_handler(MessageHandler(Filters.command, commands))
dispatcher.add_handler(MessageHandler(Filters.text, buyruq))
dispatcher.add_handler(CallbackQueryHandler(query_handler))

updater.start_polling()
updater.idle()


