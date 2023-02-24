import json
from dataBase import commands

import requests
import json
import delorean
from datetime import datetime

from service import make_request


def time():
    now = datetime.now()
    dt = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)

    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)


def start():
    now = datetime.now()
    print(now.month, now.day)
    dt = datetime(now.year, 1, 1)

    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)


async def add_db(id_data):
    s = make_request()
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        'Content-Type': 'application/json',
    }
    product_url2 = 'https://kaspi.kz/merchantcabinet/api/order/details/%7Bstatus%7D/'+str(id_data)

    request_data = s.get(
        product_url2,
        headers=headers2,
        cookies=s.cookies.get_dict()
    )

    with open('my_product_detail.json', 'w', encoding='utf-8') as my_json:
        json.dump(request_data.json(), my_json, ensure_ascii=False, indent=4)


async def readfile(lst):
    try:
        for i in lst:
            # if int(i['orderCode']) not in await commands.get_data_info2():
            await add_db(i['orderCode'])
            with open("my_product_detail.json", "r", encoding='utf-8') as data2:
                data2 = json.load(data2)
                if int(i['purchaserPhoneNumber']) not in await commands.get_data_info2():
                    db = {}
                    db['id'] = int(data2['orderId'])
                    db['name'] = data2['purchaserLastName'] + ' ' + data2['purchaserFirstName']
                    db['phone'] = data2['purchaserPhoneNumber']
                    db['product'] = data2['products'][0]['masterProduct']['name']
                    db['sku'] = data2['products'][0]['sku']
                    db['status'] = data2['deliveryMode']
                    db['price'] = data2['localizedSum']
                    try:
                        db['address'] = data2['deliveryAddress']['formattedAddress']
                    except:
                        db['address'] = "null"
                    await commands.add_deatil(db)
                    print("add success")
                else:
                    print("уже есть")
    except:
        pass


async def add_user_base():
    with open("my_product_1.json", "r", encoding='utf-8') as data:
        data_j1 = json.load(data)
        for i in range(len(data_j1)):
            try:
                info = data_j1[i]['orders']
                await readfile(info)
            except:
                pass


    with open("my_product_2.json", "r", encoding='utf-8') as data:
        data_j1 = json.load(data)
        try:
            info = data_j1['orders']
            await readfile(info)
        except:
            pass

    with open("my_product_3.json", "r", encoding='utf-8') as data:
        data_j1 = json.load(data)
        for i in range(len(data_j1)):
            try:
                info = data_j1[i]['orders']
                await readfile(info)
            except:
                pass