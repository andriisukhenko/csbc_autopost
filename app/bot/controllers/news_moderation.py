from app.handlers.news import AcceptNewsHandler, DeclineNewsHandler, RegenerateNewsHandler
from app.bot import bot
from app.models import get_db

class NewsModerationController:
    async def publish(self, message, news_id: int):
        db = next(get_db())
        handler = AcceptNewsHandler(news_id, db)
        handler(message=message, bot=bot)

    async def decline(self, message, news_id: int):
        db = next(get_db())
        handler = DeclineNewsHandler(news_id, db)
        handler(message=message)

    async def regenarate(self, message, news_id: int):
        db = next(get_db())
        handler = RegenerateNewsHandler(news_id, db)
        handler(message=message)

news_moderation_controller = NewsModerationController()