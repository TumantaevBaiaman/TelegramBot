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

API_TOKEN = '6144023875:AAGC6nGMYiK3qVP0TVWphYfs0rsr27FAIoA'
AUTHORIZED_USER_ID = ['5004318545', '5314738288']

# Configure logging
logging.basicConfig(level=logging.INFO)

bot = Bot(API_TOKEN)
dp = Dispatcher(bot)
dp.middleware.setup(LoggingMiddleware())

dp.storage = MemoryStorage()

scheduled_chats = set()
run_scheduler = False
text_start = """
 Инструкция бота:
🕔 Если выбрать «каждый час» отчёт будет отправляться каждый час
🕔 Если выбрать «каждый 3 час» отчёт будет отправляться каждый 3 час
🕔 Если вырать «2 раза в день» отчет будет отправляться с временами 8:00 и 18:00
🕔 Если вырать «3 раза в день» отчет будет отправляться временами 8:00 и 12:00 и 18:00
🔵 stop отвечает за остановку задачи. Если выбрали какой-то интервал  и хотите выбрать другую, нужно сначала остановить нажав на кнопку «stop» и потом запускать нажав  на интервалом который хотите 
🗂 «БД клиентов»  отправляет весь список клиентов
✔️ Так же следует заметить, что время работы и отдыха бота зависит от конкретных интервалов.
"""

def upload_file():
    s = make_request()
    headers2 = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/70.0.3538.77 Safari/537.36",
        # 'Content-Type': 'multipart/form-data',
        # "Accept": "application/json"
    }
    file_url = 'https://kaspi.kz/merchantcabinet/api/offer/upload'

    with open('ExcelFormatTemplate.xlsx', 'rb') as f:
        payload = {"fileData": ('ExcelFormatTemplate.xlsx', f, 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')}
        response = s.post(file_url, headers=headers2, files=payload)
    print(response.status_code)

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
    file, file2 = await get_report_file(data['offers'])
    with open('ExcelFormatTemplate.xlsx', 'wb') as f:
        f.write(file)
    await bot.send_document(chat_id=chat_id, document=open('ExcelFormatTemplate.xlsx', 'rb'))


async def send_message(chat_id):
    data = make_json_file()
    now = datetime.now().strftime("%m/%d/%Y %H:%M:%S")
    #await bot.send_message(chat_id=chat_id, text=f"Current time: {now}\nПодождите 5 мин, проводится операция")
    file, file2 = await get_report_file(data['offers'])
    with open('ExcelFormatTemplate.xlsx', 'wb') as f:
        f.write(file2)
    with open('ExcelFormatTemplateDraft.xlsx', 'wb') as f:
        f.write(file)
    upload_file()
    await bot.send_document(chat_id=chat_id, document=open('ExcelFormatTemplateDraft.xlsx', 'rb'))


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
    elif interval==7:
        n = 5
        for i in range(7):
            aioschedule.every().day.at(f"{n}:45").do(send_message, chat_id)
            n+=3
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
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        global run_scheduler
        if run_scheduler==True:
            await bot.send_message(message.from_user.id, text="Error started")
        else:
            run_scheduler = True
            asyncio.ensure_future(aioschedule_interval(24, message.from_user.id))
            text = f"Scheduling interval set to {60} minutes."
            await bot.send_message(message.from_user.id, text=text)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(Text(equals='каждый 3 час'), state=None)
async def every_hour(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        global run_scheduler
        if run_scheduler==True:
            await bot.send_message(message.from_user.id, text="Error started")
        else:
            run_scheduler = True
            asyncio.ensure_future(aioschedule_interval(7, message.from_user.id))
            text = f"Scheduling interval set to {3} hour."
            await bot.send_message(message.from_user.id, text=text)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(Text(equals='2 раза в день (8:00, 18:00)'), state=None)
async def two_day(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        global run_scheduler
        if run_scheduler==True:
            await bot.send_message(message.from_user.id, text="Error started")
        else:
            run_scheduler = True
            asyncio.ensure_future(aioschedule_interval(2, message.from_user.id))
            text = f"Send {2} message every day"
            await bot.send_message(message.from_user.id, text=text+"( 8:00, 18:00 )")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(Text(equals='3 раза в день (8:00, 12:00, 18:00)'), state=None)
async def three_day(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        global run_scheduler
        if run_scheduler==True:
            await bot.send_message(message.from_user.id, text="Error started")
        else:
            run_scheduler = True
            asyncio.ensure_future(aioschedule_interval(3, message.from_user.id))
            text = f"Send {3} message every day"
            await bot.send_message(message.from_user.id, text=text+" (8:00, 12:00, 18:00) ")
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(Text(equals='stop'), state=None)
async def three_day(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        aioschedule.clear()
        global run_scheduler
        run_scheduler = False
        text = f"Send message stop"
        await bot.send_message(message.from_user.id, text=text)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(commands='tasks')
async def test(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        tasks = aioschedule.next_run()
        text = "следующий запланированный задача: "+str(tasks)
        await bot.send_message(message.from_user.id, text=text)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")

@dp.message_handler(commands='moment')
async def test(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        await send_message_testbot(message.from_user.id)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")


@dp.message_handler(Text(equals='БД клиентов'), state=None)
async def three_day(message: types.Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        await bot.send_message(message.from_user.id, text="Подождите немного")
        await try_api()
        await asyncio.wait_for(add_user_base(), timeout=50000)
        await export_data()
        await bot.send_document(chat_id=message.from_user.id, document=open('info_user.xlsx', 'rb'))
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")


@dp.message_handler(commands='start')
async def cmd_schedule(message: Message):
    if str(message.from_user.id) in AUTHORIZED_USER_ID:
        await bot.send_message(
            chat_id=message.chat.id,
            text=text_start,
            reply_markup=buttons_key)
    else:
        await bot.send_message(chat_id=message.from_user.id, text="Sorry, you are not authorized to use this bot.")


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
