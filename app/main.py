from site_parser.parsing import NewsPageParser, MainPageParser
from site_parser.stroring import StoreNews
from app.models import News
from app.chat_openai import chat
from app.settings import settings
from telegram.bot import bot
from telegram.runner import run_bot
from telegram.moderation_handlers import SendToModeratorsHandler
from typing import List
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

class App:
    def __init__(self, 
                ParseNewsFactory: NewsPageParser,
                main_page_parser: MainPageParser,
                store_news: StoreNews
            ) -> None:
        self.NewsPageParserFactory = ParseNewsFactory
        self.main_page_parser = main_page_parser
        self.store_news = store_news

    async def start(self) -> None:
        print('app start')
        parsed_news = await self.parse_news()
        print("Parsed news", parsed_news)
        stored_news = await self.store_news(parsed_news)
        await self.send_news_to_moderation(stored_news)
    
    async def send_news_to_moderation(self, news_list: List[News]) -> List[dict]:
        news_handler = SendToModeratorsHandler(news = news_list, bot=bot)
        return await news_handler()

    async def parse_news(self):
        ids = await self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ await parser() for parser in parsers ]
    
scheduler = AsyncIOScheduler()
app = App(ParseNewsFactory=NewsPageParser, main_page_parser=MainPageParser(), store_news=StoreNews(chat=chat))

async def main():
    scheduler.add_job(app.start, trigger='cron', minute=f'*/{settings.app.PARSE_INTERVAL}')
    scheduler.start()
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())