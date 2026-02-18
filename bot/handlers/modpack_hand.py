from aiogram import  Router, Bot, F
from aiogram.types import Message, CallbackQuery, InputMediaAnimation, InputMediaPhoto

from bot.database.db_modpacks import get_modpacks_by_category, get_modpack
from bot.keyboard.mod_kb import categories_keyboard as catg_kb, modpacks_keyboard, modpack_action_keyboard
from bot.database.db_modpacks import download_modpack

rout = Router()

user_category = {}

# ID гифки (анимации) для категорий
ANIMATION_ID = 'CgACAgIAAxkBAAIFeWmTOI8rUEqesgsGG8ZavQvFu1-BAALalwACB4OZSA89BB0Sq-HROgQ'

@rout.callback_query(F.data == 'modpack')
async def donate_handler(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Тут все категории мод-паков',
            parse_mode='HTML'
        ),
            reply_markup = await catg_kb()
    )

@rout.callback_query(F.data.startswith('modcat_'))
async def category_handler(callback: CallbackQuery):
    category = callback.data.split('_', 1)[1]
    user_category[callback.from_user.id] = category

    modpacks = await get_modpacks_by_category(category)

    if not modpacks:
        await callback.answer('В этой категории пусто!', show_alert=True)
        return

    # Исправлено: используем edit_media с анимацией вместо edit_caption
    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption=f'<tg-emoji emoji-id="5415881196783565278">📂</tg-emoji>Категория: {category}\n\nВыберите модпак:',
            parse_mode='HTML'
        ),
        reply_markup=await modpacks_keyboard(category)
    )
    await callback.answer()


@rout.callback_query(F.data.startswith('mod_'))
async def mods_in_category(callback: CallbackQuery):
    modpack_id = int(callback.data.split('_')[1])
    modpack = await get_modpack(modpack_id)

    if not modpack:
        await callback.answer('❌ Модпак не найден!', show_alert=True)
        return

    caption = (
        f'<tg-emoji emoji-id="5294223696913787467">📦</tg-emoji><b>{modpack["name"]}</b>\n\n'
        f'<tg-emoji emoji-id="5415781605081906093">📝</tg-emoji> {modpack["description"] or "Без описания"}\n'
        f'<tg-emoji emoji-id="5415881196783565278">🔢</tg-emoji>Версия: {modpack["version"] or "Не указана"}\n'
        f'<tg-emoji emoji-id="5416002800192616632">📂</tg-emoji>Категория: {modpack["category"]}'
    )

    if modpack['photo_id']:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=modpack['photo_id'],
                caption=caption,
                parse_mode='HTML'
            ),
            reply_markup=await modpack_action_keyboard(modpack_id)
        )
    else:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=await modpack_action_keyboard(modpack_id),
            parse_mode='HTML'
        )

    await callback.answer()

@rout.callback_query(F.data.startswith('dlmod_'))
async def download_mod_handler(callback: CallbackQuery, bot: Bot):
    modpack_id = int(callback.data.split('_')[1])
    modpack = await download_modpack(bot, modpack_id, callback.message.chat.id)
    if modpack:
        await callback.answer('Файл отправлен')
    else:
        await callback.answer('Ошибка скачивания', show_alert=True)

@rout.callback_query(F.data == 'back_modpacks')
async def back_to_modpacks(callback: CallbackQuery):
    category = user_category.get(callback.from_user.id)
    if category:
        # Исправлено: возвращаемся к гифке через edit_media
        await callback.message.edit_media(
            media=InputMediaAnimation(
                media=ANIMATION_ID,
                caption=f'<tg-emoji emoji-id="5415881196783565278">📂</tg-emoji> Категория: {category}\n\nВыберите модпак:',
                parse_mode='HTML'
            ),
            reply_markup=await modpacks_keyboard(category)
        )
    else:
        await callback.message.edit_media(
            media=InputMediaAnimation(
                media=ANIMATION_ID,
                caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Выберите категорию:',
                parse_mode='HTML'
            ),
            reply_markup=await catg_kb()
        )
    await callback.answer()

@rout.callback_query(F.data == 'back_categories')
async def back_to_categories(callback: CallbackQuery):
    # Исправлено: возвращаемся к гифке через edit_media
    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Тут все категории мод-паков',
            parse_mode='HTML'
        ),
        reply_markup=await catg_kb()
    )
    await callback.answer()