from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaAnimation, InputMediaPhoto

from bot.keyboard.addon_kb import addons_keyboard, addon_categories_keyboard, addon_action_keyboard
from bot.database.db_addons import get_addons_by_category, get_addon
from bot.database.db_addons import download_addon

rt = Router()

user_addon_category = {}

#айди гифки
ANIMATION_ID = 'CgACAgIAAxkBAAIFeWmTOI8rUEqesgsGG8ZavQvFu1-BAALalwACB4OZSA89BB0Sq-HROgQ'

#обработчик калбека аддонов
@rt.callback_query(F.data == 'addon')
async def addon_handler(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Тут все категории аддонов',
            parse_mode='HTML'
        ),
            reply_markup = await addon_categories_keyboard()
    )

#что находиться в самой категории
@rt.callback_query(F.data.startswith('addoncat_'))
async def addon_category_handler(callback: CallbackQuery):
    category = callback.data.split('_', 1)[1]
    user_addon_category[callback.from_user.id] = category
    addons = await get_addons_by_category(category)
    if not addons:
        await callback.answer('В этой категории пусто!', show_alert=True)
        return

    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption=f'<tg-emoji emoji-id="5416002800192616632">📂</tg-emoji>Категория: {category}\n\nВыберите аддон:',
            parse_mode='HTML'
        ),
        reply_markup=await addons_keyboard(category)
    )
    await callback.answer()

@rt.callback_query(F.data.startswith('addon_'))
async def addons_in_category(callback: CallbackQuery):
    addon_id = int(callback.data.split('_')[1])
    addon = await get_addon(addon_id)

    if not addon:
        await callback.answer('❌ Аддон не найден!', show_alert=True)
        return

    caption = (
        f'<tg-emoji emoji-id="5294223696913787467">📦</tg-emoji><b>{addon["name"]}</b>\n\n'
        f'<tg-emoji emoji-id="5415781605081906093">📝</tg-emoji> {addon["description"] or "Без описания"}\n'
        f'<tg-emoji emoji-id="5415881196783565278">🔢</tg-emoji>Версия: {addon["version"] or "Не указана"}\n'
        f'<tg-emoji emoji-id="5416002800192616632">📂</tg-emoji>Категория: {addon["category"]}'
    )
    if addon['photo_id']:
        await callback.message.edit_media(
            media=InputMediaPhoto(
                media=addon['photo_id'],
                caption=caption,
                parse_mode='HTML'
            ),
            reply_markup=await addon_action_keyboard(addon_id)
        )
    else:
        await callback.message.edit_caption(
            caption=caption,
            reply_markup=await addon_action_keyboard(addon_id),
            parse_mode='HTML'
        )

    await callback.answer()

@rt.callback_query(F.data.startswith('dladdon_'))
async def download_addon_handler(callback: CallbackQuery, bot: Bot):
    addon_id = int(callback.data.split('_')[1])
    addon = await download_addon(bot, addon_id, callback.message.chat.id)
    if addon:
        await callback.answer('Файл отправлен')
    else:
        await callback.answer('Ошибка скачивания', show_alert=True)

@rt.callback_query(F.data == 'back_addons')
async def back_to_addons(callback: CallbackQuery):
    category = user_addon_category.get(callback.from_user.id)
    if category:
        # Исправлено: возвращаемся к гифке
        await callback.message.edit_media(
            media=InputMediaAnimation(
                media=ANIMATION_ID,
                caption=f'<tg-emoji emoji-id="5416002800192616632">📂</tg-emoji>Категория: {category}\n\nВыберите аддон:',
                parse_mode='HTML'
            ),
            reply_markup=await addons_keyboard(category)
        )
    else:
        await callback.message.edit_media(
            media=InputMediaAnimation(
                media=ANIMATION_ID,
                caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Выберите категорию:',
                parse_mode='HTML'
            ),
            reply_markup=await addon_categories_keyboard()
        )
    await callback.answer()

@rt.callback_query(F.data == 'back_addon_categories')
async def back_to_addon_categories(callback: CallbackQuery):
    await callback.message.edit_media(
        media=InputMediaAnimation(
            media=ANIMATION_ID,
            caption='<tg-emoji emoji-id="5415881196783565278">👇</tg-emoji>Тут все категории аддонов',
            parse_mode='HTML'
        ),
        reply_markup=await addon_categories_keyboard()
    )
    await callback.answer()