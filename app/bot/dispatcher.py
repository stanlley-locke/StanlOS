from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties

from app.core.config import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

from app.bot.handlers import chat, knowledge_base, media, academic, gamification, devops, start, finance, crm

dp = Dispatcher()

dp.include_router(start.router)
dp.include_router(finance.router)
dp.include_router(crm.router)
dp.include_router(knowledge_base.router)
dp.include_router(media.router)
dp.include_router(academic.router)
dp.include_router(gamification.router)
dp.include_router(devops.router)
dp.include_router(chat.router)

async def set_webhook():
    if settings.WEBHOOK_URL:
        url = f"{settings.WEBHOOK_URL}/webhooks/telegram"
        await bot.set_webhook(
            url=url,
            allowed_updates=dp.resolve_used_update_types(),
            drop_pending_updates=True
        )

async def delete_webhook():
    await bot.delete_webhook(drop_pending_updates=True)
