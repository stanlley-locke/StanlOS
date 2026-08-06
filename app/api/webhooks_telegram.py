from fastapi import APIRouter, Request
from aiogram.types import Update
import logging

from app.bot.dispatcher import dp, bot

logger = logging.getLogger(__name__)
router = APIRouter()

@router.post("/webhooks/telegram")
async def telegram_webhook(request: Request):
    """
    Handle incoming updates from Telegram.
    """
    try:
        update_data = await request.json()
        update = Update(**update_data)
        await dp.feed_update(bot=bot, update=update)
        return {"ok": True}
    except Exception as e:
        logger.error(f"Error handling Telegram webhook: {e}")
        return {"ok": False, "error": str(e)}
