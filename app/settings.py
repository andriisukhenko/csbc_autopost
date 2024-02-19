from dotenv import load_dotenv
from dataclasses import dataclass, field
from collections import defaultdict

load_dotenv()

@dataclass(frozen=True)
class App:
    START_URL: str = 'http://csbc.edu.ua/'
    NEWS_URL_PART: str = 'fullnews.php?news='
    LINK_SELECTOR: str = f'a[href^="{NEWS_URL_PART}"]'
    NEWS_SELECTORS: defaultdict[dict] = field(default_factory = lambda: {
        "title": '.content h2',
        "image": '.content .preview img',
        "content": '.content .one_half:not(.first)'
    })

@dataclass(frozen=True)
class Settings:
    app: App = App()

settings = Settings()