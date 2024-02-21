from typing import Any, List
from aiogram import Bot
from app.models import get_db, News, Image
from sqlalchemy.orm import Session
from app.chat_openai import chat, ChatGPT
from app.models import News
from app.settings import settings

class CreateNews:
    def __init__(self, chat: ChatGPT) -> None:
        self.chat = chat

    def filter(self, db: Session, news: List[dict]) -> List[dict]:
        existing_news = db.query(News.news_id).filter(News.news_id.in_([ item["data"]["news_id"] for item in news ])).all()
        existing_news_ids = [ news.news_id for news in existing_news ]
        return [ item for item in news if item["data"]["news_id"] not in existing_news_ids ]

    def create(self, news_data_list: List[dict]) -> List[dict]:
        db = next(get_db())
        new_news = self.filter(db, news_data_list)
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
    
class SendToModerators:
    def __init__(self, news: List[News], bot: Bot) -> None:
        self.news = news
        self.bot = bot
        self.moderators = settings.tgBot.MODERATORS

    def __call__(self):
        return self.moderators

create_news_handler = CreateNews(chat=chat)