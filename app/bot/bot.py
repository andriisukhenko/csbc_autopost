from aiogram import Bot, Dispatcher
from app.settings import settings

bot = Bot(token=settings.tgBot.TOKEN)
dp = Dispatcher()