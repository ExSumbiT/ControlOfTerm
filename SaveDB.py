import json
import firebase_admin
from firebase_admin import db

databaseURL = 'https://ctdb-70025-default-rtdb.firebaseio.com/'
cred = firebase_admin.credentials.Certificate("ctdb-70025-firebase-adminsdk-r4376-621ae0d310.json")
firebase_admin.initialize_app(cred, {'databaseURL': databaseURL})
ref = db.reference("/")


data_dict = {}


def fb_get():
    with open('data.json', 'w') as database:
        json.dump(ref.get(), database)


def fb_set():
    with open('data.json', 'r') as database:
        file_contents = json.load(database)
    ref.set(file_contents)


def last_id():
    fb_get()
    try:
        with open('data.json', 'r') as database:
            load = json.load(database)
            return int(list(load.items())[-1][0].replace('s', ''))
    except:
        return 0


def local_save(data: dict):
    global data_dict
    data_dict[f"s{last_id()+1}"] = data
    load = data_dict.copy()
    try:
        with open('data.json', 'r') as database:
            load = json.load(database)
        load.update(data_dict)
    except:
        pass
    with open('data.json', 'w') as database:
        json.dump(load, database)
    fb_set()
    return True


def update_save(data: dict):
    with open('data.json', 'r') as database:
        load = json.load(database)
    for k, v in load.items():
        if data['bar code'] == v['bar code']:
            load[k] = data
    with open('data.json', 'w') as database:
        json.dump(load, database)


def load_data():
    with open('data.json', 'r') as database:
        data = json.load(database)
    return list(iter(data.values()))
