import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from hand.hand import r

from config import TOKEN

bot = Bot(token=TOKEN)

storage = MemoryStorage()

dp = Dispatcher(storage=storage)

async def main() -> None:
    dp.include_router(r)
    await dp.start_polling(bot)


if __name__ == "__main__":

    try:
        asyncio.run(main())

    except KeyboardInterrupt:

        print('Exit')