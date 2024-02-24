from aiogram import Router, types, F
from telegram.controllers import news_moderation_controller
from telegram.callbacks import NewsModerationCallback

moderation_router = Router()

@moderation_router.callback_query(NewsModerationCallback.filter(F.action == "accept"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.publish(callback, callback_data.news_id)

@moderation_router.callback_query(NewsModerationCallback.filter(F.action == "decline"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.decline(callback, callback_data.news_id)

@moderation_router.callback_query(NewsModerationCallback.filter(F.action == "regenerate"))
async def accept(callback: types.CallbackQuery, callback_data: NewsModerationCallback):
    await news_moderation_controller.regenarate(callback, callback_data.news_id)