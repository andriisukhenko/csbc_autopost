from dotenv import load_dotenv
from dataclasses import dataclass, field
from collections import defaultdict
from pathlib import Path
from typing import List
import os

load_dotenv(override=True)

@dataclass(frozen=True)
class App:
    ROOT_DIR: Path = Path(__file__).parent.parent
    DB_NAME: str = os.getenv("DB_NAME")
    DB_CONNECTION_STR: str = f"sqlite:///{ROOT_DIR}/{DB_NAME}.sqlite3"
    IMAGES_PATH: str = f"{ROOT_DIR}/storage/images"
    START_URL: str = 'http://csbc.edu.ua/'
    NEWS_URL_PART: str = 'fullnews.php?news='
    LINK_SELECTOR: str = f'a[href^="{NEWS_URL_PART}"]'
    NEWS_SELECTORS: defaultdict[dict] = field(default_factory = lambda: {
        "title": '.content h2',
        "image": '.content .preview img',
        "content": '.content .one_half:not(.first)'
    })
    PARSE_INTERVAL: int = int(os.getenv("PARSE_INTERVAL"))

@dataclass(frozen=True)
class OpenAI:
    TOKEN: str = os.getenv("OPEN_AI_TOKEN")
    MODEL: str = "gpt-4"
    SYSTEM_MESSAGE: str = """Дій як досвідчений адміністратор коледжу, що має високу кваліфікацію SMM (Social Media Marketing) менеджмера .
        Твоя задача полягає в написанні поста для соціальної мережі на основі новини, розміщеної на сайті закладу.
        Твоя цільова аудиторія - студенти, абітурієнти та їх батьки. Але пост не повинен містити прямої реклами.
        Будь креативним, але дуже відповідальним і толерантним.
        Твоя відповідь повинна містити лише текст поста.
        Жодних пропозицій щодо додавання додаткової інформації!
        Пост має складатись з 10-15 слів.
        Коли у пості згадуются імена або прізвища людей використовуй пан та пані"""

    def USER_MESSAGE(self, title, text) -> str:
        return f"""
        Заголовок новини: {title}
        Текст новини: {text}
        """

@dataclass(frozen=True)
class TgBot:
    TOKEN: str = os.getenv("TG_BOT_TOKEN")
    MODERATORS: List[str] = field(default_factory=lambda: os.getenv("TG_MODERATORS").split(","))
    CHANNELS: List[str] = field(default_factory=lambda: os.getenv("TG_CHANNELS").split(","))

@dataclass(frozen=True)
class Settings:
    app: App = App()
    openAi: OpenAI = OpenAI()
    tgBot: TgBot = TgBot()

settings = Settings()