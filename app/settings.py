from dotenv import load_dotenv
from dataclasses import dataclass, field
from collections import defaultdict
import os

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
class OpenAI:
    TOKEN: str = os.getenv("OPEN_AI_TOKEN")
    MODEL: str = "gpt-3.5-turbo"
    SYSTEM_MESSAGE: str = """Дій як досвідчений адміністратор коледжу, що має високу кваліфікацію SMM (Social Media Marketing) менеджмера .
        Твоя задача полягає в написанні поста для соціальної мережі на основі новини, розміщеної на сайті закладу.
        Твоя цільова аудиторія - студенти, абітурієнти та їх батьки. Але пост не повинен містити прямої реклами.
        Будь креативним, але дуже відповідальним і толерантним.
        Твоя відповідь повинна містити лише текст поста.
        Жодних пропозицій щодо додавання додаткової інформації!
        Не використовуй хеш-теги #"""

    def USER_MESSAGE(self, title, text) -> str:
        return f"""
        Заголовок новини: {title}
        Текст новини: {text}
        """

@dataclass(frozen=True)
class Settings:
    app: App = App()
    openAi: OpenAI = OpenAI()
    model: str = "gpt-3.5-turbo"

settings = Settings()