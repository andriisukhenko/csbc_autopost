from typing import List
from app.models import get_db, News, Image
from sqlalchemy.orm import Session
from app.chat_openai import ChatGPT
from app.models import News, Image

class StoreNews:
    def __init__(self, chat: ChatGPT) -> None:
        self.chat = chat

    async def filter(self, db: Session, news: List[dict]) -> List[dict]:
        existing_news = db.query(News.news_id).filter(News.news_id.in_([ item["data"]["news_id"] for item in news ])).all()
        existing_news_ids = [ news.news_id for news in existing_news ]
        return [ item for item in news if item["data"]["news_id"] not in existing_news_ids ]

    async def __call__(self, news_data_list: List[dict]) -> List[dict]:
        db = next(get_db())
        new_news = await self.filter(db, news_data_list)
        obj_news = []
        for data in new_news:
            data["data"]["modified_content"] = self.chat.create_content(data["data"]["title"], data["data"]["original_content"])
            news = News(**data['data'])
            img = Image(path=data["image"])
            img.news = news
            db.add(news)
            db.add(img)
            obj_news.append(news)
        db.commit()
        [ db.refresh(news) for news in obj_news ]
        return obj_news 