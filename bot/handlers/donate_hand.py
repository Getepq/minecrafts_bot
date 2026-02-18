from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery, InputMediaAnimation, LabeledPrice, PreCheckoutQuery, Message
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

from bot.keyboard.donate_kb import donate as don_kb

rout = Router()

# FSM для хранения состояния ожидания суммы
class DonateState(StatesGroup):
    waiting_for_amount = State()


@rout.callback_query(F.data == 'donate_author')
async def donate_handler(callback: CallbackQuery, bot: Bot):
    chat_id = callback.message.chat.id
    message_id = callback.message.message_id
    await bot.edit_message_media(
        chat_id=chat_id,
        message_id=message_id,
        media=InputMediaAnimation(
            media='CgACAgIAAxkBAAIFZWmTJSQolk9naWuVAkca8S4Falt-AAJTjwAC3ASYSAQe014lIP9vOgQ',
            caption='Тут вы можете меня поддержать финансово<tg-emoji emoji-id="5415740790007688659">😻</tg-emoji>\nВсе способы снизу!',
            parse_mode='HTML'
        ),
        reply_markup=don_kb
    )

@rout.callback_query(F.data.startswith('donate_'))
async def send_donate(callback: CallbackQuery, state: FSMContext):
    amount = callback.data.split("_")[1]
    #если кастом сумма
    if amount == 'custom':
        await callback.message.answer(
            'Введите сумму от 1 до 2500<tg-emoji emoji-id="5415967495561442609">😻</tg-emoji>:',parse_mode='HTML')
        await state.set_state(DonateState.waiting_for_amount)
        await callback.answer()
        return

    # Для фиксированных сумм
    await create_invoice(callback.message, amount)
    await callback.answer()


async def create_invoice(message: Message, amount: str):
    """Создание счёта на оплату"""
    prices = [LabeledPrice(label='XTR', amount=int(amount))]

    await message.answer_invoice(
        title='Продвижение автора!',
        description=f'Донат на финансовую поддержку бота в размере {amount} звёзд! Спасибо!❤️',
        prices=prices,
        provider_token='',
        payload=f'donate_payload_{amount}',
        currency='XTR',
    )


@rout.message(DonateState.waiting_for_amount)
async def process_custom_amount(message: Message, state: FSMContext):
    """Обработка введённой кастомной суммы"""
    try:
        amount = int(message.text.strip())

        # Проверка лимитов (Telegram Stars: минимум 1, максимум 2500)
        if amount < 1:
            await message.answer('Сумма не должна быть меньше 1<tg-emoji emoji-id="5415967495561442609">😻</tg-emoji>',parse_mode='HTML')
            return
        if amount > 2500:
            await message.answer('Максимальная сумма 2.500<tg-emoji emoji-id="5415967495561442609">😻</tg-emoji>',parse_mode='HTML')
            return

        # Сбрасываем состояние
        await state.clear()

        # Создаём счёт
        await create_invoice(message, str(amount))

    except ValueError:
        await message.answer("Пожалуйста, введите число!")
    except Exception:
        await message.answer('Произошла ошибка,пожалуйста,потерпите.')

@rout.pre_checkout_query()
async def pre_checkout_handler(pre_checkout_query: PreCheckoutQuery):
    await pre_checkout_query.answer(ok=True)

@rout.message(F.successful_payment)
async def success_payment_handler(message: Message):
    payment_info = message.successful_payment
    await message.answer(f"Спасибо за донат {payment_info.total_amount} звезд! 🥳")