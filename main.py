import asyncio
import logging
from bot import bot, dp

from handlers.user import user_router
from handlers.admin import admin_router

async def main():
    logging.basicConfig(
        level=logging.INFO,
        filename="logs.log",
        #filemode="w",
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        encoding="UTF-8",
        )

    dispatcher_logger = logging.getLogger('aiogram')
    dispatcher_logger.setLevel(logging.WARNING)

    dp.include_routers(admin_router, user_router)

    logging.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())
