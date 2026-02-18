from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Any, Awaitable
import time


class ThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.5):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:

        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.users:
            last_time = self.users[user_id]
            if current_time - last_time < self.rate_limit:
                await event.answer("Слишком быстро! Подождите немного.")
                return

        self.users[user_id] = current_time
        return await handler(event, data)


class CallbackThrottlingMiddleware(BaseMiddleware):
    def __init__(self, rate_limit: float = 0.3):
        self.rate_limit = rate_limit
        self.users: Dict[int, float] = {}

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:

        user_id = event.from_user.id
        current_time = time.time()

        if user_id in self.users:
            last_time = self.users[user_id]
            if current_time - last_time < self.rate_limit:
                await event.answer("Слишком быстро!", show_alert=True)
                return

        self.users[user_id] = current_time
        return await handler(event, data)