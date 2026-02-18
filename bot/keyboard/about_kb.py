from aiogram.utils.keyboard import InlineKeyboardMarkup, InlineKeyboardButton

my_bio = InlineKeyboardMarkup(inline_keyboard=[
    [InlineKeyboardButton(text='ТГК', url='https://t.me/progouME', icon_custom_emoji_id='5226614537943290981')],
    [InlineKeyboardButton(text='Предложка и лс', url='https://t.me/veryhighest', icon_custom_emoji_id='5226614537943290981')],
    [InlineKeyboardButton(text='в меню', callback_data='back_menu',icon_custom_emoji_id='5305757775752620395')]
])