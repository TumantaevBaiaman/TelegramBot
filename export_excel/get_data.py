import requests
import json
import delorean
from datetime import datetime

from service import make_request


def time():
    now = datetime.now()
    dt = datetime(now.year, now.month, now.day, now.hour, now.minute, now.second, now.microsecond)
    # dt = datetime(2022, 12, 17)
    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)


def start():
    now = datetime.now()
    # dt = datetime(2022, 12, 2)
    dt = datetime(now.year, now.month, 1)

    return int(delorean.Delorean(dt, timezone='UTC').epoch * 1000)



async def try_api():
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

    delivery_url = 'https://kaspi.kz/mc/api/orderTabs/active?count=50&selectedTabs=DELIVERY&startIndex=0&returnedToWarehouse=false'
    pickup_url = 'https://kaspi.kz/mc/api/orderTabs/active?count=50&selectedTabs=PICKUP&startIndex=0&returnedToWarehouse=false'
    archive_url = f'https://kaspi.kz/mc/api/orderTabs/archive?start=0&count=250000&fromDate={start()}&toDate={time()}&statuses=CANCELLED&statuses=COMPLETED&statuses=RETURNED&statuses=RETURN_REQUESTED&statuses=CREDIT_TERMINATION_PROCESS'

    request = s.get(
        delivery_url,
        headers=headers2,
        cookies=s.cookies.get_dict()
    )

    request2 = s.get(
        archive_url,
        headers=headers2,
        cookies=s.cookies.get_dict()
    )

    request3 = s.get(
        pickup_url,
        headers=headers2,
        cookies=s.cookies.get_dict()
    )

    with open('my_product_1.json', 'w', encoding='utf-8') as my_json:
        json.dump(request.json(), my_json, ensure_ascii=False, indent=4)

    with open('my_product_2.json', 'w', encoding='utf-8') as my_json:
        json.dump(request2.json(), my_json, ensure_ascii=False, indent=4)

    with open('my_product_3.json', 'w', encoding='utf-8') as my_json:
        json.dump(request3.json(), my_json, ensure_ascii=False, indent=4)