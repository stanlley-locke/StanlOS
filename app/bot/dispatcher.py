from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.client.default import DefaultBotProperties
from aiogram.types import BotCommand

from app.core.config import settings

bot = Bot(
    token=settings.BOT_TOKEN,
    default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)

from app.bot.handlers import chat, knowledge_base, media, academic, gamification, devops, start, finance, crm, apps

from app.bot.middlewares.rbac import RBACMiddleware

dp = Dispatcher()
dp.message.middleware(RBACMiddleware())
dp.callback_query.middleware(RBACMiddleware())
dp.include_router(start.router)
dp.include_router(apps.router)
dp.include_router(finance.router)
dp.include_router(crm.router)
dp.include_router(knowledge_base.router)
dp.include_router(media.router)
dp.include_router(academic.router)
dp.include_router(gamification.router)
dp.include_router(devops.router)
dp.include_router(chat.router)

async def set_bot_commands():
    commands = [
        BotCommand(command="start", description="Main Dashboard"),
        BotCommand(command="tasks", description="View Pending Tasks"),
        BotCommand(command="assign", description="Add New Task"),
        BotCommand(command="clear_tasks", description="Clear All Tasks"),
        BotCommand(command="finance", description="Financial Module Overview"),
        BotCommand(command="expense", description="Log Expense Manually"),
        BotCommand(command="income", description="Log Income Entry"),
        BotCommand(command="summary", description="Expense Breakdown Report"),
        BotCommand(command="history", description="Browse Recent Transactions"),
        BotCommand(command="reset_transactions", description="Reset All Transactions"),
        BotCommand(command="convert", description="FX Currency Converter"),
        BotCommand(command="crypto", description="Crypto Market Prices"),
        BotCommand(command="translate", description="AI Text Translator"),
        BotCommand(command="wiki", description="Wikipedia Concept Lookup"),
        BotCommand(command="knowledge", description="Memory & RAG Knowledge Base"),
        BotCommand(command="note", description="Save Record to Memory"),
        BotCommand(command="find", description="Semantic RAG Search"),
        BotCommand(command="crm", description="Network Intelligence CRM"),
        BotCommand(command="contact", description="Add Contact Record"),
        BotCommand(command="network", description="View Saved Contacts"),
        BotCommand(command="media", description="Media Extractor & OCR"),
        BotCommand(command="yt", description="Download Media Audio"),
        BotCommand(command="weather", description="Live Weather Forecast"),
        BotCommand(command="calculate", description="Math & Financial Calculator"),
        BotCommand(command="gamification", description="Points & Trivia Dashboard"),
        BotCommand(command="trivia", description="Challenge AI Trivia Quiz"),
        BotCommand(command="checkin", description="Daily Points Check-in"),
        BotCommand(command="memory", description="Stored Personal Facts"),
        BotCommand(command="devops", description="System Metrics & Diagnostics"),
        BotCommand(command="help", description="System Guide & Reference")
    ]
    try:
        await bot.set_my_commands(commands)
    except Exception as e:
        import logging
        logging.getLogger(__name__).warning(f"Could not set bot commands: {e}")

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
