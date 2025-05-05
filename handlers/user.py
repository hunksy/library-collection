from aiogram import types, Router
from aiogram.filters.command import Command

user_router = Router()

@user_router.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(f"Привет, {message.from_user.full_name}!")