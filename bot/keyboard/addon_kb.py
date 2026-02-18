from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db_addons import get_all_categories, get_addons_by_category, get_all_addons

async def addon_categories_keyboard():
    keyboard = InlineKeyboardBuilder()
    categories = await get_all_categories()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category,
            callback_data=f"addoncat_{category}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='в меню',
        callback_data='back_menu',
        icon_custom_emoji_id='5305757775752620395'
    ))
    return keyboard.adjust(2).as_markup()

async def addons_keyboard(category: str, prefix: str = "addon"):
    keyboard = InlineKeyboardBuilder()
    addons = await get_addons_by_category(category)
    for addon in addons:
        keyboard.add(InlineKeyboardButton(
            text=f"{addon['name']} | v{addon['version']}",
            callback_data=f"{prefix}_{addon['id']}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_addon_categories',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.adjust(1).as_markup()

async def addon_action_keyboard(addon_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='скачать',
        callback_data=f'dladdon_{addon_id}',
        icon_custom_emoji_id='5415785805559920785'
    ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_addons',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.as_markup()

async def all_addons_for_delete():
    keyboard = InlineKeyboardBuilder()
    addons = await get_all_addons()
    for addon in addons:
        keyboard.add(InlineKeyboardButton(
            text=f"Удалить: {addon['name']}",
            callback_data=f"delete_addon_{addon['id']}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_menu',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.adjust(1).as_markup()