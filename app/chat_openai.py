from openai import OpenAI, RateLimitError
from app.settings import settings

class ChatGPT:
    def __init__(self, client: OpenAI, 
                 model: str = settings.openAi.MODEL,
                 system_message: str = settings.openAi.SYSTEM_MESSAGE,
                 user_message = settings.openAi.USER_MESSAGE) -> None:
        self.client = client
        self.model = model
        self.system_message = system_message
        self.user_message = user_message

    def create_content(self, title, text):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    { "role": "system", "content": self.system_message },
                    { "role": "user" , "content": self.user_message(title, text)}
                ]
            )
            return response.choices[0].message.content
        except RateLimitError as e:
            print(e)
            return text

chat = ChatGPT(client=OpenAI(api_key=settings.openAi.TOKEN))