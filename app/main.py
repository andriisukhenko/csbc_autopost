from app.parser import NewsPageParser, MainPageParser
from app.handlers.news import create_news_handler, SendToModeratorsHandler
from typing import List
from app.bot import run_bot, bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
import asyncio

scheduler = AsyncIOScheduler()

class App:
    NewsPageParserFactory: NewsPageParser = NewsPageParser
    main_page_parser: MainPageParser = MainPageParser()

    async def start(self) -> None:
        print('app start')
        last_news = await self.load_last_news()
        print(last_news)
        await self.handle_news(last_news)

    async def handle_news(self, news_list: List[dict]) -> List[dict]:
        news = await create_news_handler.create(news_data_list=news_list)
        news_handler = SendToModeratorsHandler(news = news, bot=bot)
        return await news_handler()

    async def load_last_news(self):
        ids = await self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ await parser() for parser in parsers ]
    
    async def send_test_message(self):
        print("send test message")
        return await bot.send_message(450092520, "Test message")
    
app = App()

async def main():
    scheduler.add_job(app.start, trigger='cron', minute='*/1')
    scheduler.start()
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())