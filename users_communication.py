from aiogram import types
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher import FSMContext

from config import dp, cur, bot

"""
See profiles users
Choice doing button for communcations
"""

# base keyboard for functions on users communication
keyboard_btn = [
        [types.KeyboardButton(text='👌')],
        [types.KeyboardButton(text='✉')],
        [types.KeyboardButton(text='⏩ Наступне')],
        [types.KeyboardButton(text='◀ Назад')]
    ]

keyboard = types.ReplyKeyboardMarkup(keyboard=keyboard_btn, resize_keyboard=True)


async def random_profile(message: types.Message):
    # random search user profile and except mine
    user_id = message.from_user.id
    cur.execute(f" SELECT * FROM users WHERE id <> {user_id} ORDER BY RANDOM() LIMIT 1")

    global profiles
    profiles = cur.fetchone()

    # formating in text
    info_profile = "" 
    for i in str(profiles).split()[:-1][1:]:
        info_profile += f'{i}\n'.replace("'", '').replace(')', '')


    path_photo = str(profiles).replace(')', '').replace("'", '').split()[-1::]
    return await bot.send_photo(user_id, 
                        photo=open(str(path_photo).replace('[', '').replace(']', '').replace("'", ''), 'rb'), 
                        caption=info_profile, reply_markup=keyboard
    )


# See profiles other users (questionnaires)
@dp.message_handler(Text(equals='Подивитися профілі'))
async def see_profile(message: types.Message):
    await random_profile(message)


# Next profile
@dp.message_handler(Text(equals='⏩ Наступне'))
async def next(message: types.Message):
    # again seeing profile
    await random_profile(message)


"""
    Notify the person about the event
    After that, we write out the profile
"""
# Like profile
@dp.message_handler(Text(equals='👌'))
async def like(message: types.Message):

    # Get profile for user
    user_id = message.from_user.id

    cur.execute(f" SELECT * FROM users WHERE id = {user_id} ")
    get_profile = cur.fetchone()

    # formating in text
    info_profile = "" 
    for i in str(get_profile).split()[:-1][1:]:
        info_profile += f'{i}\n'.replace("'", '').replace(')', '')

    # to inform the user that someone liked or liked
    id_like_user = str(profiles).split()[0].replace('(', '').replace(',', '')
    await bot.send_message(id_like_user, f"Ви сподобались користувачу\n {info_profile}\n Його nickname - @{message.from_user.username}")
   
    await random_profile(message)

# save message
class SendMessage(StatesGroup):
    send_message = State()

# input meessage
@dp.message_handler(Text(equals='✉'))
async def message(message: types.Message):
    
    await message.reply('Ведіть текст письма')
    await SendMessage.send_message.set()


@dp.message_handler(state=SendMessage.send_message)
async def send_message(message: types.Message, state: FSMContext):
    # get text message
    message_text = message.text

    # Get profile for user
    user_id = message.from_user.id

    cur.execute(f" SELECT * FROM users WHERE id = {user_id} ")
    get_profile = cur.fetchone()

    # formating in text
    info_profile = "" 
    for i in str(get_profile).split()[:-1][1:]:
        info_profile += f'{i}\n'.replace("'", '').replace(')', '')

   
    # to inform the user that someone message
    id_message_user = str(profiles).split()[0].replace('(', '').replace(',', '')
    await bot.send_message(id_message_user, f"Вам письмо від\n {info_profile}\n Його nickname - @{message.from_user.username}\nПисьмо 👇\n {message_text}")
    await state.finish()
    
    await random_profile(message)