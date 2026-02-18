from aiogram import Router,F, Bot
from aiogram.types import CallbackQuery, InputMediaAnimation

from bot.keyboard.about_kb import my_bio

rout = Router()

@rout.callback_query(F.data == 'about_author')
async def donate_handler(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaAnimation(
            media='CgACAgIAAxkBAAIFOWmTCWFkqoDyHJ7iJyNXTzJl1JAUAAIjlgACCN6RSDgURBCOlEM9OgQ',
            caption='О себе могу сказать так:\n\n'
                    'Я создаю ботов в телеграм для людей и себя<tg-emoji emoji-id="5415933479420458052">😻</tg-emoji>\n\n'
                    'Вся разработка бота заняла у меня неболее 2-4 дней,старался делать на совесть<tg-emoji emoji-id="5415967014525104115">😻</tg-emoji>.\n'
                    'Вы можете в предложку кидать свои модпаки,аддоны и что вы хотите видеть в моем боте<tg-emoji emoji-id="5418232416500216511">😻</tg-emoji>!\n\n'
                    'Снизуя находиться мой ТГК ,предложка.',
            parse_mode='HTML'
        ),
            reply_markup = my_bio
    )
