from aiogram import types, Router
from aiogram.filters.command import Command
import logging

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    logging.info(f"Пользователь {message.from_user.id} использовал команду /start")

    await message.answer(f"Привет, {message.from_user.full_name}!")