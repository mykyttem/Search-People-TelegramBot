from aiogram import executor

# files
from main import *
from profile_user import *

"""
The file starts the bot
Allows you to run other files and their functionality
"""


if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)