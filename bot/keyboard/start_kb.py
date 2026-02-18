from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

start_kb = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='мод-паки', callback_data='modpack',icon_custom_emoji_id='5415710879855441529'), InlineKeyboardButton(text='аддоны', callback_data='addon', icon_custom_emoji_id='5416044289576694315')],
    [InlineKeyboardButton(text='обо мне', callback_data='about_author', icon_custom_emoji_id='5416068826724861566')],
    [InlineKeyboardButton(text='поддержать', callback_data='donate_author',icon_custom_emoji_id='5231467404311172263')]
])