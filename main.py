import asyncio
import logging
from bot import bot, dp

from handlers.user import user_router

async def main():
    logging.basicConfig(level=logging.INFO)

    dp.include_routers(user_router)

    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
