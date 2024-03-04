from typing import List
from aiogram import Bot, types
from aiogram.enums.parse_mode import ParseMode
from app.models import News
from sqlalchemy.orm import Session
from app.chat_openai import chat
from app.models import News
from app.settings import settings
from telegram.callbacks import NewsModerationCallback
from telegram.bot import bot
from abc import ABCMeta, abstractclassmethod

class NotFoundNewsExceiption(Exception):
    pass

class PrepareMessage:
    def __init__(self, news: News) -> None:
        self.news = news

    def for_telegram(self):
        return f"""
<b>{self.news.title}</b>
{ f"<a href='{self.news.images[0].path}'>&#8205;</a>" if len(self.news.images) > 0 else "" }
{self.news.modified_content}
<i></i>
<b><a href='{self.news.url}'>Новина на сайті</a></b>"""

class CreateKeyBoard:
    def __init__(self, news: News) -> None:
        self.news = news

    def news_moderation(self) -> types.InlineKeyboardMarkup:
        accept_data = NewsModerationCallback(action='accept', news_id=self.news.id).pack()
        decline_data = NewsModerationCallback(action='decline', news_id=self.news.id).pack()
        regenerate_data = NewsModerationCallback(action='regenerate', news_id=self.news.id).pack()
        buttons = [
            [
                types.InlineKeyboardButton(text="Опублікувати", callback_data=accept_data),
                types.InlineKeyboardButton(text="Відхилити", callback_data=decline_data)
            ],
            [
                types.InlineKeyboardButton(text="Перегенерувати", callback_data=regenerate_data),
                types.InlineKeyboardButton(text="Переглянути на сайті", url=self.news.url)
            ]
        ]
        return types.InlineKeyboardMarkup(inline_keyboard=buttons)    

class SendToModeratorsHandler:
    PrepareMessage = PrepareMessage
    CreateKeyboard = CreateKeyBoard

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
            keybord = self.CreateKeyboard(news)
            message = self.PrepareMessage(news)
            await self.bot.send_message(moderator_id, message.for_telegram(), parse_mode=ParseMode.HTML, reply_markup=keybord.news_moderation())

class NewsHandler(metaclass=ABCMeta):
    PrepareMessage = PrepareMessage
    CreateKeyboard = CreateKeyBoard
    bot: Bot = bot
    skiped_statuses = ['accepted', 'declined']
    success_answer = 'Дія успішна'
    failed_answer = 'Новину вже оброблено'

    def __init__(self, news_id: int, db: Session) -> None:
        self.news_id = news_id
        self.db = db
        self.channels_id = settings.tgBot.CHANNELS

    async def __call__(self, callback: types.CallbackQuery) -> News | None:
        try:
            news = await self.get_news()
            keyboard = self.CreateKeyboard(news)
            message = self.PrepareMessage(news)
            await self.handler(callback, news, keyboard, message)
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

    async def handler(self, callback: types.CallbackQuery, news: News, keyboard: CreateKeyBoard, message: PrepareMessage) -> News:
        for channel_id in self.channels_ids:
            await bot.send_message(channel_id, message.for_telegram(), parse_mode=ParseMode.HTML)
        await self.change_status(news, "accepted")
        await callback.message.delete()
        return news
    
class DeclineNewsHandler(NewsHandler):
    success_answer = "Новину відхилено"

    async def handler(self, callback: types.CallbackQuery, news: News, keyboard: CreateKeyBoard, message: PrepareMessage) -> News | None:
        await self.change_status(news, "declined")
        await callback.message.delete()
        return news
    
class RegenerateNewsHandler(NewsHandler):
    success_answer = "Новину перегенеровано"

    async def handler(self, callback: types.CallbackQuery, news: News, keyboard: CreateKeyBoard, message: PrepareMessage) -> News | None:
        news.modified_content = chat.create_content(news.title, news.original_content)
        await callback.message.edit_text(text=message.for_telegram(), parse_mode=ParseMode.HTML, reply_markup=keyboard.news_moderation())
        await self.change_status(news, "regenerated")
        return news