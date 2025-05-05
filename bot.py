from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
import os
from dotenv import load_dotenv

load_dotenv()

TOKEN=os.getenv("BOT_TOKEN")

bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode="HTML"))
dp = Dispatcher()
