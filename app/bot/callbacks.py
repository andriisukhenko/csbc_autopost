from aiogram.filters.callback_data import CallbackData

class NewsModerationCallback(CallbackData, prefix="news_moderation"):
    action: str
    news_id: int