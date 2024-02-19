from app.parser import NewsPageParser, MainPageParser
from app.chat_openai import chat, ChatGPT
from typing import List

class App:
    NewsPageParserFactory: NewsPageParser = NewsPageParser
    main_page_parser: MainPageParser = MainPageParser()
    chat: ChatGPT = chat

    def __call__(self) -> None:
        last_news = self.load_last_news()
        print(self.handle_news(last_news[1:2]))

    def handle_news(self, news: List[dict]) -> List[dict]:
        print(news)
        return [ { "org_cont": item["original_content"], "content": self.chat.create_content(item["title"], item["original_content"]) } for item in news ]


    def load_last_news(self):
        ids = self.main_page_parser()
        parsers = [ self.NewsPageParserFactory(id) for id in ids ]
        return [ parser() for parser in parsers ]
    
app = App()

if __name__ == "__main__":
    app()