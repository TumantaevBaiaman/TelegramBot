from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

every_hour = KeyboardButton('каждый час')
two_day = KeyboardButton('2 раза в день (8:00, 18:00)')
three_day = KeyboardButton('3 раза в день (8:00, 12:00, 18:00)')
stop = KeyboardButton('stop')
excel = KeyboardButton('БД клиентов')

buttons_key = ReplyKeyboardMarkup(resize_keyboard=True).add(every_hour, two_day, three_day).add(excel, stop)