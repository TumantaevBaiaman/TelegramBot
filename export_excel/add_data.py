import asyncio
import json
from dataBase import commands

import requests
import json
import delorean
from datetime import datetime, timedelta

from service import make_request


def time(day):
    now = datetime.now()
    dt = datetime(2022, 11, 17)
    one_day = timedelta(days=day)
    dt = dt + one_day
    print(dt, 1)
    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)


def start(day):
    now = datetime.now()
    dt = datetime(2022, 11, 17)
    one_day = timedelta(days=day)
    dt = dt + one_day
    # dt = datetime(now.year, now.month, 1)
    print(dt, 2)
    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)



async def try_api2(data):
    """
    https://kaspi.kz/merchantcabinet/api/order/details/%7Bstatus%7D/210056362
    https://kaspi.kz/merchantcabinet/api/order/search
    {"searchTerm":{"statuses":["ACCEPTED_BY_MERCHANT","SUSPENDED"],"term":null,"orderTab":"DELIVERY","superExpress":false,"returnedToWarehouse":false,"cityId":null,"fromDate":1658685600000,"toDate":1658826819741},"start":0,"count":10}
    """
    s = make_request()
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        'Content-Type': 'application/json',
    }

    archive_url = f'https://kaspi.kz/mc/api/orderTabs/archive?start=0&count=500&fromDate={start(data)}&toDate={time(data+1)}&statuses=CANCELLED&statuses=COMPLETED&statuses=RETURNED&statuses=RETURN_REQUESTED&statuses=CREDIT_TERMINATION_PROCESS'

    request2 = s.get(
        archive_url,
        headers=headers2,
        cookies=s.cookies.get_dict()
    )
    print(request2.json())
    with open('my_product_2.json', 'w', encoding='utf-8') as my_json:
        json.dump(request2.json(), my_json, ensure_ascii=False, indent=4)


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
        a = 0
        b1 = 0
        b2 = 0
        for i in lst:
            # if int(i['orderCode']) not in await commands.get_data_info2():
            await add_db(i['orderCode'])
            with open("my_product_detail.json", "r", encoding='utf-8') as data2:
                data2 = json.load(data2)
                a+=1
                print(a)
                if int(data2['purchaserPhoneNumber']) not in await commands.get_data_info2():
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
                    b1 +=1
                    print(b1)
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


    for i in range(1,90):
        await try_api2(i)
        with open("my_product_2.json", "r", encoding='utf-8') as data:
            data_j1 = json.load(data)
            try:
                info = data_j1['orders']
                await asyncio.wait_for(readfile(info), timeout=50000)
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