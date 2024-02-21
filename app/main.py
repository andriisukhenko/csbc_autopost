from app.parser import NewsPageParser, MainPageParser
from app.handlers.news import create_news_handler, SendToModerators
from typing import List
from settings import settings
from threading import Thread
from app.bot.bot import main as run_bot
import schedule
import time
import asyncio

class App:
    NewsPageParserFactory: NewsPageParser = NewsPageParser
    main_page_parser: MainPageParser = MainPageParser()

    def __call__(self) -> None:
        print("app start")
        last_news = self.load_last_news()
        print(self.handle_news(last_news))

    def handle_news(self, news: List[dict]) -> List[dict]:
        return create_news_handler.create(news)

    def load_last_news(self):
        ids = self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ parser() for parser in parsers ]
    
app = App()

schedule.every(settings.app.PARSE_INTERVAL).minutes.do(app)

def app_runner():
    while True:
        schedule.run_pending()
        time.sleep(1)

async def main():
    app_thread = Thread(target=app_runner)
    app_thread.start()
    await run_bot()

if __name__ == "__main__":
    asyncio.run(main())