from aiogram import Router, types, F
from app.bot.controllers.news_moderation import news_moderation_controller
from app.bot.callbacks import NewsModerationCallback

router = Router()

@router.callback_query(NewsModerationCallback.filter(F.action == "accept"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.publish(callback, callback_data.news_id)

@router.callback_query(NewsModerationCallback.filter(F.action == "decline"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.decline(callback, callback_data.news_id)

@router.callback_query(NewsModerationCallback.filter(F.action == "regenerate"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.regenarate(callback, callback_data.news_id)