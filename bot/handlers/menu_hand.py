from aiogram import  Router, Bot, F
from aiogram.filters import  CommandStart
from aiogram.types import Message, CallbackQuery, InputMediaAnimation
from bot.keyboard.start_kb import start_kb

rout = Router()

@rout.message(CommandStart())
async def cmd_start(message: Message):
    await message.answer_animation(
        animation='CgACAgIAAxkBAAIFRWmTDF4XUlGND5gJxSCJqEZ3uRpcAALYlAACB4OZSDCGnWxvJVU4OgQ',
        caption=(
            '<b>Добро пожаловать</b> <tg-emoji emoji-id="5415740790007688659">⭐</tg-emoji>\n\n'

            '<i>Этот бот создан для облегчения игры в Minecraft</i> <tg-emoji emoji-id="5415654134747528786">⭐</tg-emoji>\n\n'

            '<b>Поддерживаемые версии:</b>\n'
            '├ <tg-emoji emoji-id="5416044289576694315">📱</tg-emoji> <b>Minecraft Bedrock</b>\n'
            '└ <tg-emoji emoji-id="5415710879855441529">💻</tg-emoji> <b>Minecraft Java</b>\n\n'

            '<i>Для просмотра библиотеки мод-паков и аддонов\n'
            'выберите категорию под ваше устройство ниже</i> <tg-emoji emoji-id="5413772866057438590">👇</tg-emoji>'
        ),
        parse_mode='HTML',
        reply_markup=start_kb
    )

@rout.callback_query(F.data == 'back_menu')
async def donate_handler(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaAnimation(
            media='CgACAgIAAxkBAAIFRWmTDF4XUlGND5gJxSCJqEZ3uRpcAALYlAACB4OZSDCGnWxvJVU4OgQ',
            caption='<b>Добро пожаловать</b> <tg-emoji emoji-id="5415740790007688659">⭐</tg-emoji>\n\n'

            '<i>Этот бот создан для облегчения игры в Minecraft</i> <tg-emoji emoji-id="5415654134747528786">⭐</tg-emoji>\n\n'

            '<b>Поддерживаемые версии:</b>\n'
            '├ <tg-emoji emoji-id="5416044289576694315">📱</tg-emoji> <b>Minecraft Bedrock</b>\n'
            '└ <tg-emoji emoji-id="5415710879855441529">💻</tg-emoji> <b>Minecraft Java</b>\n\n'

            '<i>Для просмотра библиотеки мод-паков и аддонов\n'
            'выберите категорию под ваше устройство ниже</i> <tg-emoji emoji-id="5413772866057438590">👇</tg-emoji>',
            parse_mode='HTML'
        ),
            reply_markup = start_kb
    )
