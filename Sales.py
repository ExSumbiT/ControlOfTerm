import json
from SaveDB import update_save, load_data


def load_sales():
    with open('sales.json', 'r') as database:
        sales = json.load(database)
    return sales


def sub_sales():
    data = load_data()
    sales = load_sales()
    for item in data:
        if item['bar code'] in sales:
            for k in sales:
                if item['bar code'] == k:
                    item['amount'] -= sales[k]
    for _ in data:
        update_save(_)
    with open('sales.json', 'w') as database:
        json.dump({}, database)

