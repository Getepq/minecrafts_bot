from aiogram.types import InlineKeyboardButton
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.database.db_modpacks import get_all_categories, get_modpacks_by_category, get_all_modpacks


async def categories_keyboard():
    keyboard = InlineKeyboardBuilder()
    categories = await get_all_categories()
    for category in categories:
        keyboard.add(InlineKeyboardButton(
            text=category,
            callback_data=f"modcat_{category}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='в меню',
        callback_data='back_menu',
        icon_custom_emoji_id='5305757775752620395'
    ))
    return keyboard.adjust(2).as_markup()


async def modpacks_keyboard(category: str, prefix: str = "mod"):
    keyboard = InlineKeyboardBuilder()
    modpacks = await get_modpacks_by_category(category)
    for modpack in modpacks:
        keyboard.add(InlineKeyboardButton(
            text=f"{modpack['name']} | v{modpack['version']}",
            callback_data=f"{prefix}_{modpack['id']}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_categories',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.adjust(1).as_markup()


async def modpack_action_keyboard(modpack_id: int):
    keyboard = InlineKeyboardBuilder()
    keyboard.add(InlineKeyboardButton(
        text='скачать',
        callback_data=f'dlmod_{modpack_id}',
        icon_custom_emoji_id='5415785805559920785'
    ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_modpacks',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.as_markup()


async def all_modpacks_for_delete():
    keyboard = InlineKeyboardBuilder()
    modpacks = await get_all_modpacks()
    for modpack in modpacks:
        keyboard.add(InlineKeyboardButton(
            text=f"Удалить: {modpack['name']}",
            callback_data=f"delete_mod_{modpack['id']}"
        ))
    keyboard.row()
    keyboard.add(InlineKeyboardButton(
        text='назад',
        callback_data='back_menu',
        icon_custom_emoji_id='5296587908906511469'
    ))
    return keyboard.adjust(1).as_markup()