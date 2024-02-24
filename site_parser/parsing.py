from abc import ABCMeta
from typing import List, Dict
from app.settings import settings
from bs4 import BeautifulSoup, Tag
import aiohttp

class ParseRequest:
    def __init__(self, url: str, format: str = 'lxml', http: aiohttp = aiohttp, soup: BeautifulSoup = BeautifulSoup) -> None:
        self.url = url
        self.format = format
        self.http = http
        self.soup = soup

    async def __call__(self) -> BeautifulSoup:
        async with aiohttp.ClientSession() as session:
            async with session.get(self.url) as response:
                return self.soup(await response.text(), self.format)

class ParsePage(metaclass=ABCMeta):
    def __init__(self, parse_req: ParseRequest, selector: str | dict):
        self.parse_req = parse_req
        self.selector = selector
        self.resp = None

    async def __call__(self):
        resp = await self.parse_req()
        return self.post_handler(self.select(resp))
    
    def select(self, resp: BeautifulSoup) -> List[Tag] | Dict[str, Tag]:
        if type(self.selector) == str:
            return resp.select(self.selector)
        else:
            return { key: resp.select_one(value) for key, value in self.selector.items() }
        

    def post_handler(self, data: List[Tag] | Dict[str, Tag]) -> List[Tag]:
        return data

class MainPageParser(ParsePage):
    def __init__(self):
        super().__init__(parse_req = ParseRequest(settings.app.START_URL), selector = settings.app.LINK_SELECTOR)
    
    def post_handler(self, data: List[Tag]) -> List[str]:
        return [ el.attrs['href'].split("=")[1] for el in data ]
    
class NewsPageParser(ParsePage):
    def __init__(self, news_id: str | int):
        self.id = news_id
        super().__init__(
            parse_req=ParseRequest(f"{settings.app.START_URL}{settings.app.NEWS_URL_PART}{news_id}"),
            selector=settings.app.NEWS_SELECTORS
            )
        
    def post_handler(self, data: Dict[str, Tag]) -> Dict[str, str]:
        return {
            "data": {
                "news_id": int(self.id),
                "url": self.parse_req.url,
                "title": data["title"].text,
                "original_content": "".join([ item.text for item in data["content"].select("p") if item.text ]),
            },
            "image": f'{settings.app.START_URL}{data["image"].attrs["src"]}'
        }

