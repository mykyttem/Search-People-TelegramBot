from aiogram import types
from config import dp

# start
@dp.message_handler(commands=['start', 'help'])
async def send_welcome(message: types.Message):
    # buttons
    keyboard_btn = [
        [types.KeyboardButton(text='Подивитися профілі')],
        [types.KeyboardButton(text='Заповнити мій профіль')],
        [types.KeyboardButton(text='Мій профіль')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)
    await message.answer("Оберіть опцію", reply_markup=keyboard)