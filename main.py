import asyncio
import logging
from bot import bot, dp

from handlers.user import user_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.log",
        #filemode="w",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding="UTF-8",
        )

    dp.include_routers(user_router)

    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
