from app.bot.routes.news_moderation import router as news_moderation_router
from aiogram import types
from aiogram.filters.command import Command
from app.bot.bot import bot, dp
import asyncio

async def run_bot():
    print("bot start")

    @dp.message(Command("start"))
    async def cmd_start(message: types.Message):
        await message.answer("Hellow")
    
    @dp.message(Command("who_me"))
    async def cmd_who_me(message: types.Message):
        await message.answer(str(message.from_user.id))

    dp.include_routers(news_moderation_router)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(run_bot())