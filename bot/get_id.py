import asyncio
import logging

from aiogram import Bot, Dispatcher, F
from aiogram.types import Message
from aiogram.filters import CommandStart

bot = Bot(token='8508650572:AAGaPmAwAk-dZasSXPYRpXYLLPVR5KrJdPU')
dp = Dispatcher()


@dp.message(F.animation)
async def get_id(message: Message):
    await message.answer(f'id: {message.animation.file_id}')

@dp.message(CommandStart)
async def cmd_start(message: Message):
    await message.answer('был запущен файл get_id.py')

async def main():
    await dp.start_polling(bot)

if __name__ == '__main__':
    try:
        logging.basicConfig(level=logging.DEBUG)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот остановил работу.')