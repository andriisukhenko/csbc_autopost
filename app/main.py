from app.parser import NewsPageParser, MainPageParser
from app.handlers.news import create_news_handler, SendToModeratorsHandler
from typing import List
from settings import settings
from threading import Thread
from app.bot.bot import main as run_bot, bot
import schedule
import time
import asyncio

loop = None

class App:
    NewsPageParserFactory: NewsPageParser = NewsPageParser
    main_page_parser: MainPageParser = MainPageParser()

    def __call__(self) -> None:
        print('app start')
        last_news = self.load_last_news()
        self.handle_news(last_news)

    def handle_news(self, news: List[dict]) -> List[dict]:
        news_handler = SendToModeratorsHandler(news=create_news_handler.create(news_data_list=news), bot=bot)
        asyncio.run(news_handler())

    def load_last_news(self):
        ids = self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ parser() for parser in parsers ]
    
    async def send_test_message(self):
        print("send test message")
        return await bot.send_message(450092520, "Test message")
    
app = App()

schedule.every(settings.app.PARSE_INTERVAL).minutes.do(app)

def app_runner(loop: asyncio.AbstractEventLoop):
    while True:
        asyncio.set_event_loop(loop)
        loop.run_forever()
        f = asyncio.run_coroutine_threadsafe(app.send_test_message(), loop=loop)
        print(f.result())
        schedule.run_pending()
        time.sleep(1)

async def main(loop: asyncio.AbstractEventLoop):
    app_thread = Thread(target=app_runner, args=(loop,), daemon=True)
    app_thread.start()
    await run_bot()

if __name__ == "__main__":
    loop = asyncio.new_event_loop()
    asyncio.run(main(loop))