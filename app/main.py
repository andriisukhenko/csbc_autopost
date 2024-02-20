from app.parser import NewsPageParser, MainPageParser
from app.handlers.news import create_news_handler
from typing import List

class App:
    NewsPageParserFactory: NewsPageParser = NewsPageParser
    main_page_parser: MainPageParser = MainPageParser()

    def __call__(self) -> None:
        last_news = self.load_last_news()
        print(self.handle_news(last_news))

    def handle_news(self, news: List[dict]) -> List[dict]:
        return create_news_handler.create(news)

    def load_last_news(self):
        ids = self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ parser() for parser in parsers ]
    
app = App()

if __name__ == "__main__":
    app()