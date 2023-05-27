from aiogram import types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from config import dp, con, cur
from main import send_welcome


@dp.message_handler(Text(equals="Подивитися профілі"))
async def see_profile(message: types.Message):
    await message.reply("Дивимося профілі")


# fill out the profile
"""
We fill out the profile step by step 
Transfer it to the "ProfileFormState", and get
Save in Db user
"""

# Get input user
class ProfileFormState(StatesGroup):
    name = State()
    sex = State()
    age = State()
    location = State()
    description = State()


# fill in step by step
@dp.message_handler(Text(equals="Заповнити мій профіль"))
async def fill_profile(message: types.Message):

    user_id = message.from_user.id
    cur.execute(f"SELECT id FROM users WHERE id = {user_id}")
    search_user_id = cur.fetchone()

    if search_user_id:
        await message.reply("Ви вже створили анкету\n Її можно переглянути у профілі")
    else:
        await ProfileFormState.name.set()
        await message.reply("Заповнюємо профіль, введіть ім'я")


@dp.message_handler(state=ProfileFormState.name)
async def name_user(message: types.Message, state: FSMContext):
    name = message.text
    await state.update_data(name=name)

    await ProfileFormState.sex.set()
    await message.reply(f"{name}, ви M (Хлопець) чи F (Дівчині)?")


@dp.message_handler(state=ProfileFormState.sex)
async def sex_user(message: types.Message, state: FSMContext):
    sex = message.text
    await state.update_data(sex=sex)

    await ProfileFormState.age.set()
    await message.reply(f"Скільки вам років?")


@dp.message_handler(state=ProfileFormState.age)
async def age_user(message: types.Message, state: FSMContext):
    try:
        age = int(message.text)
        await state.update_data(age=age)

    except ValueError:
        await message.reply('Це не число')
        fill_profile()

    await ProfileFormState.location.set()
    await message.reply(f"Звідки ви?")


@dp.message_handler(state=ProfileFormState.location)
async def location_user(message: types.Message, state: FSMContext):
    location = message.text
    await state.update_data(location=location)

    await ProfileFormState.description.set()
    await message.reply(f"Введіть опис профілю")


@dp.message_handler(state=ProfileFormState.description)
async def description_user(message: types.Message, state: FSMContext):
    description = message.text
    await state.update_data(description=description)

    # Get all data from state
    global data_user_profile

    data_user_profile = await state.get_data()
    name = data_user_profile.get('name')
    sex = data_user_profile.get('sex')
    age = data_user_profile.get('age')
    location = data_user_profile.get('location')
    description = data_user_profile.get('description')

    await state.finish() 

    # buttons
    keyboard_btn = [
        [types.KeyboardButton(text='Так, зберегти')],
        [types.KeyboardButton(text='Ні, повернутися в меню')]
    ]
    keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)

    
    reply_text_data = f"Ім'я: {name}\n Стать:{sex}\n Вік: {age}\nЗвідки: {location}\nОпис: {description}"
    await message.reply(f'Вірно заповнена анкета?\n {reply_text_data}', reply_markup=keyboard)


# If "No" - Fill again
@dp.message_handler(Text(equals='Ні, повернутися в меню'))
async def fill_again(message: types.Message):
    await send_welcome(message)


# If 'yes' - Add data user in dataBase
@dp.message_handler(Text(equals='Так, зберегти'))
async def save_profile(message: types.Message):
   
    # data_user_profile - global variables from function "description_user"
    name = data_user_profile.get('name')
    sex = data_user_profile.get('sex')
    age = data_user_profile.get('age')
    location = data_user_profile.get('location')
    description = data_user_profile.get('description')

    user_id = message.from_user.id

    cur.execute(""" INSERT INTO users 
            (id, name, sex, age, location, description)values(?, ?, ?, ?, ?, ?);""", [user_id, name, sex, age, location, description]
    )
    con.commit()

    await message.reply('Зберегли, можеш переглянути у своєму профілі')   
    await send_welcome(message)