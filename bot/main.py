import asyncio
#import logging
import os

from aiogram import Bot, Dispatcher
from dotenv import load_dotenv

from bot.handlers.donate_hand import rout as don_rt
from bot.handlers.menu_hand import rout as start_rt
from bot.handlers.about_hand import rout as about_rt
from bot.handlers.modpack_hand import rout as modpack_rout
from bot.handlers.addon_hand import rt as addon_rout
from bot.handlers.admin_panel_mod import rt as pn_rt_mod
from bot.handlers.admin_panel_addon import rt as pn_rt_addon
from bot.middlewares.throttling import ThrottlingMiddleware,CallbackThrottlingMiddleware

from bot.database.db_modpacks import create_db as create_modpack
from bot.database.db_addons import create_db as create_addon

load_dotenv()

bot = Bot(token=os.getenv('TOKEN'))
dp = Dispatcher()

async def main():
    dp.message.middleware(ThrottlingMiddleware(rate_limit=0.5))
    dp.callback_query.middleware(CallbackThrottlingMiddleware(rate_limit=0.3))

    await create_modpack()
    await create_addon()
    print('DB created.')

    dp.include_router(start_rt)
    dp.include_router(don_rt)
    dp.include_router(about_rt)
    dp.include_router(modpack_rout)
    dp.include_router(addon_rout)
    dp.include_router(pn_rt_mod)
    dp.include_router(pn_rt_addon)

    await dp.start_polling(bot)


if __name__ == '__main__':
    try:
        #logging.basicConfig(level=logging.DEBUG)
        asyncio.run(main())
    except KeyboardInterrupt:
        print('бот остановил работу.')


