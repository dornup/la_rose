from aiogram import Bot, Dispatcher, types
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from bs4 import BeautifulSoup
from lxml.html.soupparser import fromstring
from secret import *
import requests
import asyncio
import logging


# ------- settings ----------
logging.basicConfig(level="INFO")  # TODO: когда допилим подключить к log.log

bot = Bot(token=TOKEN)
dp = Dispatcher()

class MyCallBack(CallbackData, prefix='my'):
    data: str
# ---------------------------

# ------- parsing (getting photos) -------
#TODO: попросить папу выложить фотки и отпарсить их
site = requests.get("https://novosibirsk.la-rose.ru/catalog/bukety-nedeli/")
txt = BeautifulSoup(site.text, 'html.parser')
elem = fromstring(str(txt))
links = elem.xpath('//*[@class="thumb shine"]/img/@src')
links = map(lambda x: "https://novosibirsk.la-rose.ru" + x , links)
for i, link in enumerate(links):
    img = requests.get(link)
    if img.status_code == 200:
        with open(f"images/{i}.jpg", 'wb') as file:
            file.write(img.content)
            logging.info(f"картинка {i} успешно скачана")

# ----------------------------------------

#-------- commands --------
@dp.message(Command("start"))
async def initialisation(message: types.Message):
    button = types.InlineKeyboardButton(text="Подтвердить", callback_data=MyCallBack(data="accept").pack())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])  
  
    await message.answer(text='''Это бот La Rose
Пожалуйста, подтвердите согласие на доступ к вашим персональным данным (username в телеграмм, номер телефона)''',
                           reply_markup=keyboard)
    
@dp.callback_query(MyCallBack.filter(F.data == "accept"))
async def answer_button(call: types.CallbackQuery):
    await call.message.answer(text='''Спасибо!''')
    await call.answer()
    await call.message.answer(text='''Приветственное сообщение''')

#--------------------------

# ------- start polling----
async def main():
    await dp.start_polling(bot)  


if __name__ == '__main__':
    asyncio.run(main())
# -------------------------
