from telegram.moderation_handlers import AcceptNewsHandler, DeclineNewsHandler, RegenerateNewsHandler
from aiogram import types
from app.models import get_db

class NewsModerationController:
    async def publish(self, callback: types.CallbackQuery, news_id: int):
        db = next(get_db())
        handler = AcceptNewsHandler(news_id, db)
        await handler(callback=callback)

    async def decline(self, callback: types.CallbackQuery, news_id: int):
        db = next(get_db())
        handler = DeclineNewsHandler(news_id, db)
        await handler(callback=callback)

    async def regenarate(self, callback: types.CallbackQuery, news_id: int):
        db = next(get_db())
        handler = RegenerateNewsHandler(news_id, db)
        await handler(callback=callback)

news_moderation_controller = NewsModerationController()