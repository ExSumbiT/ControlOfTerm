import time
import telebot
from SaveDB import local_save, last_id
import datetime
import schedule
from threading import Thread
from time import sleep


def schedule_checker():
    while True:
        schedule.run_pending()
        sleep(1)


bot = telebot.TeleBot('token')


data_dict = {}
message_id = None


def init(zero_dict: dict):
    global data_dict
    zero_dict['id'] = last_id() + 1
    zero_dict['name'] = None
    zero_dict['bar code'] = None
    zero_dict['amount'] = None
    zero_dict['doArrival'] = datetime.date.today()
    zero_dict['expiration date'] = 0
    zero_dict['doManufacture'] = None
    zero_dict['best before'] = None
    zero_dict['chat_id'] = None
    zero_dict['days before'] = False
    zero_dict['hours of start'] = False


@bot.message_handler(regexp="stop")
def stop(message):
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id.id)


@bot.message_handler(commands=['start'])
def start_message(message):
    try:
        init(data_dict)
        global message_id
        bot.delete_message(message.chat.id, message.id)
        message_id = bot.send_message(message.chat.id, 'Enter "Bar code"')
        if 'stop' in message.text.lower():
            stop(message)
            return False
        bot.register_next_step_handler(message_id, bar_code)
    except:
        bot.edit_message_text('O-op-ps-s, something went wrong!', message_id.chat.id, message_id.id)
        time.sleep(3)
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message_id.id)


def bar_code(message):
    try:
        data_dict['bar code'] = message.text
        data_dict['chat_id'] = message.chat.id
        bot.edit_message_text('Enter "Amount"', message_id.chat.id, message_id.id)
        if 'stop' in message.text.lower():
            stop(message)
            return False
        bot.delete_message(message.chat.id, message.id)
        bot.register_next_step_handler(message_id, amount)
    except:
        bot.edit_message_text('O-op-ps-s, something went wrong!', message_id.chat.id, message_id.id)
        time.sleep(3)
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message_id.id)


def amount(message):
    try:
        data_dict['amount'] = int(message.text)
        bot.edit_message_text('Enter date\n"best before" - dd.mm.yyyy\n'
                              'date of manufacture with expiration date - dd.mm.yyyy, dd'
                              '\n*just expiration date if DOM is today - dd',
                              message_id.chat.id, message_id.id)
        if 'stop' in message.text.lower():
            stop(message)
            return False
        bot.delete_message(message.chat.id, message.id)
        bot.register_next_step_handler(message_id, date)
    except:
        bot.edit_message_text('O-op-ps-s, something went wrong!', message_id.chat.id, message_id.id)
        time.sleep(3)
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message_id.id)


def date(message):
    try:
        if len(message.text) > 3:
            if len(message.text) > 11:
                dates = str(message.text).split(',')
                data_dict['doManufacture'] = datetime.datetime.strptime(dates[0], '%d.%m.%Y').date()
                data_dict['expiration date'] = int(dates[1])
                data_dict['best before'] = (data_dict['doManufacture'] +
                                            datetime.timedelta(data_dict['expiration date']))
            else:
                data_dict['doManufacture'] = data_dict['doArrival']
                data_dict['best before'] = (datetime.datetime.strptime(message.text, '%d.%m.%Y')).date()
        else:
            data_dict['doManufacture'] = data_dict['doArrival']
            data_dict['expiration date'] = int(message.text)
            data_dict['best before'] = (data_dict['doManufacture'] +
                                        datetime.timedelta(data_dict['expiration date']))
        if data_dict['best before'] < datetime.date.today():
            bot.edit_message_text('O-op-ps-s, incorrect date!', message_id.chat.id, message_id.id)
            time.sleep(3)
            bot.delete_message(message.chat.id, message.id)
            bot.delete_message(message.chat.id, message_id.id)
            return False
        data_dict['best before'] = data_dict['best before'].isoformat()
        data_dict['doManufacture'] = data_dict['doManufacture'].isoformat()
        data_dict['doArrival'] = data_dict['doArrival'].isoformat()
        if 'stop' in message.text.lower():
            stop(message)
            return False
        bot.delete_message(message.chat.id, message.id)
        local_save(data_dict.copy())
        bot.edit_message_text('Date saved!', message_id.chat.id, message_id.id)
        time.sleep(3)
        bot.delete_message(message.chat.id, message_id.id)
    except:
        bot.edit_message_text('O-op-ps-s, something went wrong!', message_id.chat.id, message_id.id)
        time.sleep(3)
        bot.delete_message(message.chat.id, message.id)
        bot.delete_message(message.chat.id, message_id.id)


@bot.message_handler(commands=['end'])
def end(message):
    from TelegramNT import validate, ending
    end_msg = validate(message)
    bot.register_next_step_handler(end_msg, ending)


@bot.message_handler(commands=['set'])
def param(message):
    global message_id
    from Setings import set_param
    message_id = set_param(message)
    bot.register_next_step_handler(message_id, get_param)


def get_param(message):
    global message_id
    global data_dict
    bot.delete_message(message.chat.id, message_id.id)
    bot.delete_message(message.chat.id, message.id)
    message_id = bot.send_message(message.chat.id, "Enter value:")
    data_dict[f'{message.text}'] = True
    bot.register_next_step_handler(message_id, save_param)


def save_param(message):
    from Setings import save
    bot.edit_message_text('Params saved!', message.chat.id, message_id.id)
    sleep(3)
    bot.delete_message(message.chat.id, message.id)
    bot.delete_message(message.chat.id, message_id.id)
    for k, v in data_dict.items():
        if v is True:
            data_dict[k] = message.text
    save(data_dict)


if __name__ == "__main__":
    from TelegramNT import function_to_run
    schedule.every().minute.do(function_to_run)
    Thread(target=schedule_checker).start()
    bot.polling(none_stop=True)
