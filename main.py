import sys
import io
import asyncio
import logging
import nest_asyncio

from aiogram import Bot, Dispatcher
import config
from handlers import router

nest_asyncio.apply()

# объекты бота и диспетчера, в бота нужно передать токен
bot = Bot(config.TOKEN)
dp = Dispatcher()
dp.include_router(router)                                 # подключает к диспетчеру все обработчики, кот используют router        
        
# функция запуска бота
async def main() -> None:
    await bot.delete_webhook(drop_pending_updates=True)     # удалить все обновления, кот-е произошли после last завершения бота
    await dp.start_polling(bot, skip_updates=True)


logging.basicConfig(level=logging.INFO, stream=sys.stdout, force=True)
asyncio.run(main())
