import os
from aiogram import types

from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

from config import dp, con, cur, bot
from main import send_welcome

# fill out the profile
"""
We fill out the profile step by step 
Transfering it to the "ProfileFormState", and get
Save in Db user
"""

# Get input user
class ProfileFormState(StatesGroup):
    name = State()
    sex = State()
    age = State()
    location = State()
    description = State()
    photo_path = State()


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
async def block_steps_fill(message: types.Message, state: FSMContext):

    # functions for steps
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
            return
           
        await ProfileFormState.location.set()
        await message.reply(f"Звідки ви?")


    @dp.message_handler(state=ProfileFormState.location)
    async def location_user(message: types.Message, state: FSMContext):
        location = message.text
        await state.update_data(location=location)

        await ProfileFormState.photo_path.set()
        await message.reply(f"Добавьте Фото")


    @dp.message_handler(content_types=types.ContentTypes.PHOTO | types.ContentTypes.DOCUMENT, state=ProfileFormState.photo_path)
    async def photo_user(message: types.Message, state: FSMContext):
        if message.photo:
            # Get photo (of the highest quality)
            photo = message.photo[-1]  
        elif message.document:
            photo = message.document
        else:
            await message.reply("Будь ласка, надішліть фотографію або документ зображення")
            return

        photo_id = photo.file_id

        # save photo and path
        photo_path = os.path.join('photos', f'{photo_id}.jpg')
        await photo.download(photo_path)
        await state.update_data(photo_path=photo_path)

        await ProfileFormState.description.set()
        await message.reply(f"Введіть опис профілю")


    @dp.message_handler(state=ProfileFormState.description)
    async def description_user(message: types.Message, state: FSMContext):
        description = message.text
        await state.update_data(description=description)

        # buttons
        keyboard_btn = [
            [types.KeyboardButton(text='Так, зберегти')],
            [types.KeyboardButton(text='Ні, повернутися в меню')],
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)

        # Get all data from state
        global dict_user_profile
        data_user_profile = await state.get_data()

        dict_user_profile = {
            'photo_path': data_user_profile.get('photo_path'),
            'name': data_user_profile.get('name'),
            'sex': data_user_profile.get('sex'),
            'age': data_user_profile.get('age'),
            'location': data_user_profile.get('location'),
            'description': data_user_profile.get('description')
        }
        await state.finish() 

        # message
        reply_text_data = f"""
            Ім'я: {dict_user_profile['name']}
            Стать:{dict_user_profile['sex']} 
            Вік: {dict_user_profile['age']} 
            Звідки: {dict_user_profile['location']}
            Опис: {dict_user_profile['description']}
        """

        await bot.send_message(message.from_user.id, 'Вірно заповнена анкета?')

        photo_path = os.path.join(os.getcwd(), dict_user_profile['photo_path'])
        await bot.send_photo(message.from_user.id, photo=open(photo_path, 'rb'), caption=reply_text_data, reply_markup=keyboard)

        # If "No" - Fill again
        @dp.message_handler(Text(equals='Ні, повернутися в меню'))
        async def fill_again(message: types.Message):
            os.remove(dict_user_profile['photo_path'])
            await send_welcome(message)


        # If 'yes' - Add data user in dataBase
        @dp.message_handler(Text(equals='Так, зберегти'))
        async def save_profile(message: types.Message):

            user_id = message.from_user.id

            cur.execute(f"SELECT id FROM users WHERE id = {user_id}")
            search_user_id = cur.fetchone()

            if not search_user_id:

                # if user create profile
                cur.execute(""" INSERT INTO users 
                    (id, name, sex, age, location, description, photo_path)values(?, ?, ?, ?, ?, ?, ?);""", 
                    [
                        user_id, 
                        dict_user_profile['name'], 
                        dict_user_profile['sex'], 
                        dict_user_profile['age'], 
                        dict_user_profile['location'], 
                        dict_user_profile['description'],
                        dict_user_profile['photo_path']
                    ]
                )
                con.commit()

                await message.reply('Зберегли, можеш переглянути у своєму профілі')   
                await send_welcome(message)
            else:

                # if user update profile
                cur.execute(f""" UPDATE users SET name = ?, sex = ?, age = ?, location = ?, description = ?, photo_path = ? WHERE id = {user_id}""", 
                    (
                        dict_user_profile['name'], 
                        dict_user_profile['sex'], 
                        dict_user_profile['age'], 
                        dict_user_profile['location'], 
                        dict_user_profile['description'],
                        dict_user_profile['photo_path']
                    )
                )
                con.commit()
                os.remove(dict_user_profile['photo_path'])
                await message.reply('Дані оновлені')
                await send_welcome(message)


"""
Informations for my account 
Settings
"""

# Checking my profile
@dp.message_handler(Text(equals='Мій профіль'))
async def checking_my_profile(message: types.Message):

    # Get profile for user
    user_id = message.from_user.id

    cur.execute(f" SELECT * FROM users WHERE id = {user_id} ")
    get_profile = cur.fetchone()
    con.commit()

    if not get_profile:
        await message.reply('У вас немає профіля')
        await send_welcome(message)
    else:
        # formating in text
        info_profile = "" 
        for i in str(get_profile).split()[:-1][1:]:
            info_profile += f'{i}\n'.replace("'", '').replace(')', '')


        # buttons
        keyboard_btn = [
            [types.KeyboardButton(text='Видалити мій профіль')],
            [types.KeyboardButton(text='Заповнити заново')],
            [types.KeyboardButton(text='◀ Назад')]
        ]
        keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)
        
        path_photo = str(get_profile).replace(')', '').replace("'", '').split()[-1::]
        await bot.send_photo(user_id, 
                            photo=open(str(path_photo).replace('[', '').replace(']', '').replace("'", ''), 'rb'), 
                            caption=info_profile, reply_markup=keyboard
        )
    

@dp.message_handler(Text(equals='Видалити мій профіль'))
async def delete_my_profile(message: types.Message):

    # Get profile for user
    user_id = message.from_user.id
    cur.execute(f" SELECT photo_path FROM users WHERE id = {user_id} ")

    path_photo_user = cur.fetchone()
    os.remove(str(path_photo_user).replace('(', '').replace(')', '').replace("'", '').replace(',', ''))

    cur.execute(f" DELETE FROM users WHERE id = {user_id} ")
    con.commit()

    await message.reply('Ваш профіль видалений')
    await send_welcome(message)


@dp.message_handler(Text(equals='Заповнити заново'))
async def edit_profile(message: types.Message):

    """
    We call the "fill_profile" function so as not to copy the steps
    """

    await ProfileFormState.name.set()
    await message.reply("Заповнюємо профіль, введіть ім'я")

    # call out functions
    await block_steps_fill()