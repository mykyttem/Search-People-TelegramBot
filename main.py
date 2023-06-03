from aiogram import types
from aiogram.dispatcher.filters import Text

from config import dp, cur, con
from locales import dict_string

"""
File for main functions
initial buttons
Main functionals 
"""

""" term translation, term key, and to which to translate """
def translation(text_key, language) -> dict:
    return dict_string[text_key].get(language, '')

def user_language(id_user) -> str:
    cur.execute(f"SELECT language FROM language_users WHERE id_user = {id_user};")
    get_language = cur.fetchone()
    con.commit()
    
    if get_language:
        # Get value language
        return get_language[0]


# beginning
@dp.message_handler(commands=['start'])
async def choice_languages(message: types.Message):
    # buttons for select languages
    select_btn_languages = [
        [types.KeyboardButton(text='Українська 🇺🇦')],
        [types.KeyboardButton(text='English 🇺🇸')]
    ]
    btn_languages = types.ReplyKeyboardMarkup(keyboard=select_btn_languages, resize_keyboard=True)
    await message.answer('Оберіть мову / select languages', reply_markup=btn_languages)


"""
    User select language
    Save in DB user id and language
    If user not select - save
    if update language - delete current, and select
"""

# start 
@dp.message_handler(Text(equals=['Українська 🇺🇦', 'English 🇺🇸']))
async def send_welcome(message: types.Message):
    id_user = message.from_user.id
    language = user_language(id_user)

    keyboard_btn = [
        [types.KeyboardButton(text=translation('Подивитися профілі', language))],
        [types.KeyboardButton(text=translation('Заповнити мій профіль', language))],
        [types.KeyboardButton(text=translation('Мій профіль', language))],
        [types.KeyboardButton(text=translation('Змінити мову', language))]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)

    
    if not language:           
        if message.text == 'Українська 🇺🇦':
            cur.execute(f"INSERT INTO language_users (id_user, language) values (?, ?);", [id_user, 'uk'])
            con.commit()

            await send_welcome(message)

        elif message.text == 'English 🇺🇸':
            cur.execute(f"INSERT INTO language_users (id_user, language) values (?, ?);", [id_user, 'en'])
            con.commit()

            await send_welcome(message)
    else:
        await message.answer(translation("Оберіть опцію", language), reply_markup=keyboard)


# change language
@dp.message_handler(Text(equals=['Змінити мову', 'Change language']))
async def change_language(message: types.Message):
    id_user = message.from_id
    cur.execute(f" DELETE FROM language_users WHERE id_user = {id_user}")
    con.commit()
   
    await choice_languages(message)
    

# button back menu
@dp.message_handler(Text(equals=["◀ Назад", '◀ back', '◀']))
async def back(message: types.Message):
    await send_welcome(message)