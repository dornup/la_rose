from aiogram import Bot, Dispatcher, types, Router
from aiogram import F
from aiogram.filters.callback_data import CallbackData
from aiogram.filters.command import Command
from aiogram.utils.media_group import MediaGroupBuilder
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.state import State, StatesGroup
from aiogram.fsm.context import FSMContext
from bs4 import BeautifulSoup
from lxml.html.soupparser import fromstring
from typing import Dict, Any
from secret import *
import requests
import asyncio
import logging
import datetime
from datetime import datetime, timedelta
import pytz


# ------- settings ----------
logging.basicConfig(level="INFO")  # TODO: когда допилим подключить к l.log

bot = Bot(token=TOKEN)
dp = Dispatcher()
form_router = Router()
dp.include_router(form_router)

index = 0

class MyCallBack(CallbackData, prefix='my'):
    data: str
    number: str = ""
    name: str = ""
    phone: str = ""
    adress: str = ""
    date: str = ""
    time: str = ""

class Form(StatesGroup):
    number = State()
    name = State()
    phone = State()
    adress = State()
    date = State()
    time = State()

even_hours = [0, 2, 4, 6, 8, 10, 12, 14, 16, 18, 20, 22, 0]
# ---------------------------

# ------- parsing (getting photos) -------
#TODO: пока закомментила парсинг, потом будет другой источник и другие фотки
# site = requests.get("https://novosibirsk.la-rose.ru/catalog/bukety-nedeli/")
# txt = BeautifulSoup(site.text, 'html.parser')
# elem = fromstring(str(txt))
# links = elem.xpath('//*[@class="thumb shine"]/img/@src')
# links = map(lambda x: "https://novosibirsk.la-rose.ru" + x , links)
# for i, link in enumerate(links):
#     img = requests.get(link)
#     if img.status_code == 200:
#         with open(f"imgs/{i}.jpg", 'wb') as file: #!!
#             file.write(img.content)
#             logging.info(f"картинка {i} успешно скачана")

# ----------------------------------------

#-------- commands --------
@dp.message(Command("start"))
async def initialisation(message: types.Message):
    global index
    index = 0
    button = types.InlineKeyboardButton(text="Подтвердить", callback_data=MyCallBack(data="accept").pack())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])  
  
    await message.answer(text='''Это бот La Rose
Пожалуйста, подтвердите согласие на доступ к вашим персональным данным (username в телеграмм, номер телефона)''',
                           reply_markup=keyboard)
    
@dp.callback_query(MyCallBack.filter(F.data == "accept"))
async def answer_button(call: types.CallbackQuery):
    await call.message.answer(text='''Спасибо!''')
    button = types.InlineKeyboardButton(text='Посмотреть витрину', callback_data=MyCallBack(data='catalog').pack())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
    await call.message.answer(text='''Приветственное сообщение''',
                              reply_markup=keyboard)
    
@dp.callback_query(MyCallBack.filter(F.data == 'catalog'))
async def catalog(call: types.CallbackQuery):
    global index
    button1 = types.InlineKeyboardButton(text='Выбрать букет', callback_data=MyCallBack(data='choose').pack())
    button2 = types.InlineKeyboardButton(text='Посмотреть еще', callback_data=MyCallBack(data='catalog').pack())
    button3 = types.InlineKeyboardButton(text='Связаться с администратором', callback_data=MyCallBack(data='admin').pack(), url='https://t.me/Meladze_dorn')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard = [[button1, button2],[button3]])
    media = MediaGroupBuilder()
    for i in range(index, index+9):
        media.add_photo(media=types.FSInputFile(f'C:\\Users\\Admin\\Desktop\\vsc_projects\\la_rose\\imgs\\{i}.jpg')) # !!!!!!!!!!
    index += 9
    await call.message.answer_media_group(media=media.build())
    await call.message.answer(text='Выберите действие:', reply_markup=keyboard)

@dp.callback_query(MyCallBack.filter(F.data == 'choose'))
async def choose(call: types.CallbackQuery, state: FSMContext):
    await state.set_state(Form.number)
    await call.message.answer(text=f'''Пожалуйста, введите цифру от 1 до {index}''')

@form_router.message(Form.number)
async def name(message: types.Message, state: FSMContext):
    await state.update_data(number = message.text)
    await state.set_state(Form.name)
    button = types.InlineKeyboardButton(text='Связаться с администратором', callback_data=MyCallBack(data='admin').pack(), url='https://t.me/Meladze_dorn')
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button]])
    if message.text.isnumeric():
        if (index - 8) <= int(message.text) <= index:
            await message.answer(text='''Отлично, вас поняли, пожалуйста, введите свое имя''')
        else:
            await message.answer(text='''Что-то пошло не так, перенаправляю вас на администратора''', reply_markup=keyboard)
    else: 
        await message.answer(text='''Что-то пошло не так, перенаправляю вас на администратора''', reply_markup=keyboard)

@form_router.message(Form.name)
async def phone(message: types.Message, state: FSMContext):
    await state.update_data(name = message.text)
    await state.set_state(Form.phone)
    await message.answer(f'''Приятно познакомиться, {message.text}!
Пожалуйста, укажите номер телефона получателя, чтобы мы могли связаться с ним''')

@form_router.message(Form.phone)
async def phone(message: types.Message, state: FSMContext):
    await state.update_data(phone = message.text)
    await state.set_state(Form.adress)
    button = types.KeyboardButton(text='Адрес нужно уточнить по телефону', callback_data=MyCallBack(data='unknown_adress').pack())
    keyboard = types.ReplyKeyboardMarkup(keyboard=[[button]])
    await message.answer(f'''Хорошо, давайте определим, на какой адрес нужно отправить букет. Введите адрес получателя в формате: улица, номер дома, квартира. Если вы не знаете адрес получателя, то нажмите на кнопку "Адрес нужно уточнить по телефону"''', reply_markup=keyboard)

@form_router.message(Form.adress)
async def date(message: types.Message, state: FSMContext):
    await state.update_data(adress = message.text)
    await state.set_state(Form.date)
    start = datetime.today()
    date_list = [(start.date() + timedelta(days=i)).strftime('%d.%m.%Y') for i in range(30)]
    keyboard = ReplyKeyboardBuilder()
    for i, date in enumerate(date_list):
        button = types.KeyboardButton(text=date)
        keyboard.add(button)
    keyboard.adjust(3, repeat=True)
    await message.answer(text='Выберите дату', reply_markup=keyboard.as_markup())

@form_router.message(Form.date)
async def time(message: types.Message, state: FSMContext):
    await state.update_data(date = message.text)
    await state.set_state(Form.time)
    keyboard = ReplyKeyboardBuilder()
    if message.text == datetime.today().strftime('%d.%m.%Y'):
        time_now_str = datetime.now(pytz.timezone('Asia/Novosibirsk')).strftime('%H:%M')
        hour, minutes = time_now_str.split(":")
        hour = int(hour) if int(minutes) == 0 else int(hour) + 1
        hour = hour + 1 if hour not in even_hours else hour
        for i, h in enumerate(even_hours[even_hours.index(hour):12]):
            button = types.KeyboardButton(text=f'{str(h).rjust(2, "0")}.00 - {str(even_hours[even_hours.index(hour):][(i+1)]).rjust(2, "0")}.00')
            keyboard.add(button)
    else:
        for i, h in enumerate(even_hours[:12]):
            button = types.KeyboardButton(text=f'{str(h).rjust(2, "0")}.00 - {str(even_hours[(i+1)]).rjust(2, "0")}.00')
            keyboard.add(button)
    keyboard.adjust(3)
    await message.answer(text='Выберите, пожалуйста время доставки', reply_markup=keyboard.as_markup())
    
@form_router.message(Form.time)
async def finish(message: types.Message, state: FSMContext):
    data = await state.update_data(time = message.text)
    print(data)
    await state.clear()
    await check(message, data)

async def check(message: types.Message, data: Dict[str, Any]):
    number = data['number']
    name = data['name']
    phone = data['phone']
    adress = data['adress']
    date = data['date']
    time = data['time']
    button1 = types.InlineKeyboardButton(text='Все верно', callback_data=MyCallBack(data = "send", number=number, name=name, phone=phone, adress=adress, date=date, time=time).pack())
    button2 = types.InlineKeyboardButton(text='Связаться с администратором', callback_data=MyCallBack(data = "wrong").pack())
    keyboard = types.InlineKeyboardMarkup(inline_keyboard=[[button1, button2]])
    mes = f'''
    имя: {name}
    номер букета: {number}
    номер телефона получателя: {phone}
    адрес доставки: {adress}
    дата доставки: {date}
    время доставки: {time}'''
    await message.answer(text=f'''Пожалуйста, проверьте, что все данные для заказа указаны корректно:''' + mes, reply_markup=keyboard)


@dp.callback_query(MyCallBack.filter(F.data == 'send'))
async def send(call: types.CallbackQuery, callback_data: dict):
    data = callback_data.get('info')
    number = data['number']
    name = data['name']
    phone = data['phone']
    adress = data['adress']
    date = data['date']
    time = data['time']
    await bot.send_message(chat_id=-4873594805, text=f'''имя: {name}
    номер букета: {number}
    номер телефона получателя: {phone}
    адрес доставки: {adress}
    дата доставки: {date}
    время доставки: {time}''')

@dp.callback_query(MyCallBack.filter(F.data == 'wrong'))
async def replace(call: types.CallbackQuery):
    pass

#--------------------------

# ------- start polling----
async def main():
    await dp.start_polling(bot)  


if __name__ == '__main__':
    asyncio.run(main())
# -------------------------
