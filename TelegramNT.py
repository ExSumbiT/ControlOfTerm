from TelegramDG import bot
import json
from datetime import date
from telebot import types
from Sales import sub_sales
from SaveDB import load_data, update_save


pinned = []
end_msg = None


def load_pinned():
    global pinned
    try:
        with open('pinned.json', 'r') as pin:
            pinned = json.load(pin)['p']
    except:
        pass


def save_pinned(pinned):
    with open('pinned.json', 'w') as pin:
        json.dump({'p': pinned}, pin)


def check_data():
    to_notify = []
    with open('data.json', 'r') as database:
        data = json.load(database)
    for k, v in data.items():
        if (date.fromisoformat(v['best before']) - date.today()).days <= 2:
            to_notify.append(v)
    return to_notify


def notify(obj_list: list):
    for obj in obj_list:
        text = f'''[{obj['id']}]Hey, "{obj['name']}" left {(date.fromisoformat
                                                          (obj['best before']) - date.today()).days} days!
Bar-code: {obj['bar code']} 
Amount: {obj['amount']}
Best before: {obj['best before']}
    DO SOMETHING!!!'''
        msg = bot.send_message(obj['chat_id'], f'{text}')
        bot.pin_chat_message(obj['chat_id'], msg.id)
        pinned.append({obj['id']: msg.id})
    save_pinned(pinned)
    return True


def function_to_run():
    sub_sales()
    load_pinned()
    obj_list = check_data()
    if obj_list:
        notify(obj_list)
    return True


def validate(message):
    load_pinned()
    global end_msg
    markup = types.ReplyKeyboardMarkup(row_width=3)
    for msg in pinned:
        markup.add(types.KeyboardButton(f'{next(iter(msg.keys()))}'))
    end_msg = bot.send_message(message.chat.id, "Choose id to end:", reply_markup=markup)
    bot.delete_message(message.chat.id, message.id)
    return end_msg


def ending(message):
    for msg in pinned:
        if message.text in msg:
            try:
                bot.delete_message(message.chat.id, msg[message.text])
                bot.delete_message(message.chat.id, msg[message.text]+1)
            except:
                pass
            del msg[message.text]
    bot.delete_message(message.chat.id, end_msg.id)
    bot.delete_message(message.chat.id, message.id)
    save_pinned([i for i in pinned if i])


def remove(id: int):
    try:
        data = load_data()
        for _ in data:
            if id == _['id']:
                del data[f's{id}']
        data = [i for i in data if i]
        for _ in data:
            update_save(_)
        return "All O`k!"
    except:
        return 'SOMETHING WENT WRONG!'
