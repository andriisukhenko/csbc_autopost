from typing import List
from aiogram import Bot, types
from aiogram.enums.parse_mode import ParseMode
from app.models import get_db, News, Image
from sqlalchemy.orm import Session
from app.chat_openai import chat, ChatGPT
from app.models import News, Image
from app.settings import settings
from app.bot.callbacks import NewsModerationCallback
from app.bot.bot import bot
from abc import ABCMeta, abstractclassmethod

class NotFoundNewsExceiption(Exception):
    pass

class ParseMessageMixin:
    def prepare_message(self, news: News):
        return f"""
<b>{news.title}</b>
{ f"<a href='{news.images[0].path}'>&#8205;</a>" if len(news.images) > 0 else "" }
{news.modified_content}
<i></i>
<b><a href='{news.url}'>Новина на сайті</a></b>"""
    
    def create_keyboard(self, news: News) -> types.InlineKeyboardMarkup:
        buttons = [
            [
                types.InlineKeyboardButton(text="Опублікувати", callback_data=NewsModerationCallback(action='accept', news_id=news.id).pack()),
                types.InlineKeyboardButton(text="Відхилити", callback_data=NewsModerationCallback(action='decline', news_id=news.id).pack())
            ],
            [
                types.InlineKeyboardButton(text="Перегенерувати", callback_data=NewsModerationCallback(action='regenerate', news_id=news.id).pack()),
                types.InlineKeyboardButton(text="Переглянути на сайті", url=news.url)
            ]
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)

class CreateNews:
    def __init__(self, chat: ChatGPT) -> None:
        self.chat = chat

    async def filter(self, db: Session, news: List[dict]) -> List[dict]:
        existing_news = db.query(News.news_id).filter(News.news_id.in_([ item["data"]["news_id"] for item in news ])).all()
        existing_news_ids = [ news.news_id for news in existing_news ]
        return [ item for item in news if item["data"]["news_id"] not in existing_news_ids ]

    async def create(self, news_data_list: List[dict]) -> List[dict]:
        db = next(get_db())
        new_news = await self.filter(db, news_data_list)
        obj_news = []
        for data in new_news:
            data["data"]["modified_content"] = chat.create_content(data["data"]["title"], data["data"]["original_content"])
            news = News(**data['data'])
            img = Image(path=data["image"])
            img.news = news
            db.add(news)
            db.add(img)
            obj_news.append(news)
        db.commit()
        [ db.refresh(news) for news in obj_news ]
        return obj_news
    
class SendToModeratorsHandler(ParseMessageMixin):
    def __init__(self, news: List[News], bot: Bot) -> None:
        self.news = news
        self.bot = bot
        self.moderators = settings.tgBot.MODERATORS

    async def __call__(self):
        return [ await self.send_news(news) for news in self.news ]
     
    async def send_news(self, news: News):
        for moderator_id in self.moderators:
            print("message for:", moderator_id)
            print("message id:", news.news_id)
            print("message text:", len(news.modified_content))
            keybord = self.create_keyboard(news)
            return await self.bot.send_message(moderator_id, self.prepare_message(news), parse_mode=ParseMode.HTML, reply_markup=keybord)

class NewsHandler(ParseMessageMixin, metaclass=ABCMeta):
    bot: Bot = bot
    skiped_statuses = ['accepted', 'declined']
    success_answer = 'Дія успішна'
    failed_answer = 'Новину вже оброблено'

    def __init__(self, news_id: int, db: Session) -> None:
        self.news_id = news_id
        self.db = db
        self.channels_id = settings.tgBot.CHANNELS

    async def __call__(self, *args, callback: types.CallbackQuery, **kwargs) -> News | None:
        try:
            await self.handler(*args, callback, **kwargs)
            await callback.answer(self.success_answer)
        except NotFoundNewsExceiption:
            await callback.answer(self.failed_answer)
            await callback.message.delete()

    @abstractclassmethod
    async def handler(self, *args, **kwargs):
        pass

    async def get_news(self):
        news = self.db.query(News).filter(News.id == self.news_id, News.status.not_in(self.skiped_statuses)).first()
        if not news:
            raise NotFoundNewsExceiption
        return news

    async def change_status(self, news: News | None, status: str):
        if not news:
            news = self.get_news()
        news.status = status
        self.db.commit()
        self.db.refresh(news)
        return news

class AcceptNewsHandler(NewsHandler):
    success_answer = "Новина відправлена на публікацію"
    channels_ids = settings.tgBot.CHANNELS

    async def handler(self, callback: types.CallbackQuery) -> News:
        news: News = await self.get_news()
        for channel_id in self.channels_ids:
            await bot.send_message(channel_id, self.prepare_message(news), parse_mode=ParseMode.HTML)
        await self.change_status(news, "accepted")
        await callback.message.delete()
        return news
    
class DeclineNewsHandler(NewsHandler):
    success_answer = "Новину відхилено"

    async def handler(self, callback: types.CallbackQuery) -> News | None:
        news: News = await self.get_news()
        await self.change_status(news, "declined")
        await callback.message.delete()
        return news
    
class RegenerateNewsHandler(NewsHandler):
    success_answer = "Новину перегенеровано"

    async def handler(self, callback: types.CallbackQuery) -> News | None:
        news: News = await self.get_news()
        news.modified_content = chat.create_content(news.title, news.original_content)
        await callback.message.edit_text(text=self.prepare_message(news), parse_mode=ParseMode.HTML, reply_markup=self.create_keyboard(news))
        await self.change_status(news, "regenerated")
        return news
        

create_news_handler = CreateNews(chat=chat)