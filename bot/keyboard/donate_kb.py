from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

donate = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='donationalerts', url='https://www.donationalerts.com/r/timye', icon_custom_emoji_id='5231467404311172263')],
    [InlineKeyboardButton(text='5', callback_data='donate_5',icon_custom_emoji_id='5415967495561442609'),
     InlineKeyboardButton(text='10', callback_data='donate_10',icon_custom_emoji_id='5415967495561442609')],
    [InlineKeyboardButton(text='25', callback_data='donate_25',icon_custom_emoji_id='5415967495561442609'),
     InlineKeyboardButton(text='40', callback_data='donate_40',icon_custom_emoji_id='5415967495561442609')],
    [InlineKeyboardButton(text='50', callback_data='donate_50',icon_custom_emoji_id='5415967495561442609')],
    [InlineKeyboardButton(text='своя сумма', callback_data='donate_custom',icon_custom_emoji_id='5415967495561442609')],
    [InlineKeyboardButton(text='в меню', callback_data='back_menu',icon_custom_emoji_id='5305757775752620395')]
])
