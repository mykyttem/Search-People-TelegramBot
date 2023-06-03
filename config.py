import sqlite3
import logging

from aiogram import Bot, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

API_TOKEN = 'your_token'

# Configure logging
logging.basicConfig(level=logging.INFO)

# Initialize bot and dispatcher
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot, storage=MemoryStorage())


# connect DB
con = sqlite3.connect("users.db")
cur = con.cursor()

# create TABLES
# profile user
cur.execute("""CREATE TABLE IF NOT EXISTS users(
    id INTEGER,
    name TEXT,
    sex TEXT,
    age INTEGER,
    location TEXT,
    description TEXT,
    photo_path TEXT
)""")


# choise language user
cur.execute("""CREATE TABLE IF NOT EXISTS language_users(
    id_user INTEGER PRIMARY KEY,
    language TEXT
)""")