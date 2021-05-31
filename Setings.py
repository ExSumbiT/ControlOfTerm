from telebot import types
from TelegramDG import bot


msg = None
param_dict = {'name': None, 'amount': None, 'days before': None, 'hours of start': None}


def set_param(message):
    global msg
    markup = types.ReplyKeyboardMarkup(row_width=2)
    b1 = types.KeyboardButton('name')
    b2 = types.KeyboardButton('amount')
    b3 = types.KeyboardButton('days before')
    b4 = types.KeyboardButton('hours of start')
    markup.add(b1, b2, b3, b4)
    msg = bot.send_message(message.chat.id, "Choose to edit:", reply_markup=markup)
    bot.delete_message(message.chat.id, message.id)
    return msg


def save(data):
    global param_dict
    param_dict.update(data)

