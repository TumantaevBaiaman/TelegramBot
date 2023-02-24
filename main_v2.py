import asyncio
import json
import logging
from datetime import datetime
from aiogram.dispatcher.filters import Text

import aioschedule
from aiogram import Bot, Dispatcher, executor, types
from aiogram.contrib.middlewares.logging import LoggingMiddleware
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, CallbackQuery

from button import buttons_key
from export_excel.add_data import add_user_base
from export_excel.excel import export_data
from export_excel.get_data import try_api
from report import get_report_file
from service import make_request

API_TOKEN = '5925973975:AAEC4C1beejuIb7x1WW9_i8TrJ2s_KUyW1s'

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

dp.storage = MemoryStorage()

scheduled_chats = set()
run_scheduler = False

def make_json_file():
    s = make_request()
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        'Content-Type': 'application/json',
    }
    product_url = 'https://kaspi.kz/merchantcabinet/api/offer'
    request = s.post(
        product_url,
        headers=headers2,
        cookies=s.cookies.get_dict(),
        data=json.dumps({
            'offerStatus': "ACTIVE",
            'start': 0,
            'count': 200
        })

    )
    with open('my_product.json', 'w', encoding='utf-8') as my_json:
        json.dump(request.json(), my_json, ensure_ascii=False, indent=4)
    return request.json()

async def send_message_testbot(chat_id):
    data = make_json_file()
    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    await bot.send_message(chat_id=chat_id, text=f"Current time: {now}\nПодождите 5 мин, проводится операция")
    file = await get_report_file(data['offers'])
    with open('ExcelFormatTemplate.xlsx', 'wb') as f:
        f.write(file)
    await bot.send_document(chat_id=chat_id, document=open('ExcelFormatTemplate.xlsx', 'rb'))


async def send_message(chat_id):
    data = make_json_file()
    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    #await bot.send_message(chat_id=chat_id, text=f"Current time: {now}\nПодождите 5 мин, проводится операция")
    file = await get_report_file(data['offers'])
    with open('ExcelFormatTemplate.xlsx', 'wb') as f:
        f.write(file)
    await bot.send_document(chat_id=chat_id, document=open('ExcelFormatTemplate.xlsx', 'rb'))


async def aioschedule_interval(interval: int, chat_id: int):
    global run_scheduler
    if interval==24:
        interval_data = 23 / 23
        for i in range(24):
            data = int(i*interval_data)
            if data==0:
                data='00'
            aioschedule.every().day.at(f"{data}:45").do(send_message, chat_id)
    elif interval==2:
        aioschedule.every().day.at(f"7:45").do(send_message, chat_id)
        aioschedule.every().day.at(f"17:45").do(send_message, chat_id)
    elif interval==3:
        aioschedule.every().day.at(f"7:45").do(send_message, chat_id)
        aioschedule.every().day.at(f"11:45").do(send_message, chat_id)
        aioschedule.every().day.at(f"17:45").do(send_message, chat_id)
    while run_scheduler:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


@dp.callback_query_handler(lambda c: c.data in ('24', '3', '2', 'stop'))
async def process_callback_schedule_time(callback_query: CallbackQuery):
    current_chat_id = callback_query.message.chat.id
    if callback_query.data == "stop":
        if current_chat_id in scheduled_chats:
            scheduled_chats.remove(current_chat_id)
        text = "Scheduling stopped."
    else:
        interval = int(callback_query.data)
        scheduled_chats.add(current_chat_id)
        asyncio.ensure_future(aioschedule_interval(interval, current_chat_id))
        text = f"Scheduling interval set to {interval} minutes."
    await bot.answer_callback_query(callback_query.id, text=text)


@dp.message_handler(Text(equals='каждый час'), state=None)
async def every_hour(message: types.Message):
    global run_scheduler
    if run_scheduler==True:
        await bot.send_message(message.from_user.id, text="Error started")
    else:
        run_scheduler = True
        asyncio.ensure_future(aioschedule_interval(24, message.from_user.id))
        text = f"Scheduling interval set to {60} minutes."
        await bot.send_message(message.from_user.id, text=text)


@dp.message_handler(Text(equals='2 раза в день (8:00, 18:00)'), state=None)
async def two_day(message: types.Message):
    global run_scheduler
    if run_scheduler==True:
        await bot.send_message(message.from_user.id, text="Error started")
    else:
        run_scheduler = True
        asyncio.ensure_future(aioschedule_interval(2, message.from_user.id))
        text = f"Send {2} message every day"
        await bot.send_message(message.from_user.id, text=text+"( 8:00, 18:00 )")


@dp.message_handler(Text(equals='3 раза в день (8:00, 12:00, 18:00)'), state=None)
async def three_day(message: types.Message):
    global run_scheduler
    if run_scheduler==True:
        await bot.send_message(message.from_user.id, text="Error started")
    else:
        run_scheduler = True
        asyncio.ensure_future(aioschedule_interval(3, message.from_user.id))
        text = f"Send {3} message every day"
        await bot.send_message(message.from_user.id, text=text+" (8:00, 12:00, 18:00) ")


@dp.message_handler(Text(equals='stop'), state=None)
async def three_day(message: types.Message):
    aioschedule.clear()
    global run_scheduler
    run_scheduler = False
    text = f"Send message stop"
    await bot.send_message(message.from_user.id, text=text)


@dp.message_handler(commands='tasks')
async def test(message: types.Message):
    tasks = aioschedule.next_run()
    text = "следующий запланированный задача: "+str(tasks)
    await bot.send_message(message.from_user.id, text=text)

@dp.message_handler(commands='moment')
async def test(message: types.Message):
    await send_message_testbot(message.from_user.id)


@dp.message_handler(Text(equals='БД клиентов'), state=None)
async def three_day(message: types.Message):
    await bot.send_message(message.from_user.id, text="Подождите немного")
    await try_api()
    await add_user_base()
    await export_data()
    await bot.send_document(chat_id=message.from_user.id, document=open('info_user.xlsx', 'rb'))


@dp.message_handler(commands='start')
async def cmd_schedule(message: Message):
    await bot.send_message(
        chat_id=message.chat.id,
        text='Choose a time interval:',
        reply_markup=buttons_key)


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
