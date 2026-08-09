import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from fastapi.responses import HTMLResponse

from app.core.config import settings
from app.api import webhooks_telegram, webhooks_sms, webhooks_github, dashboard_api
from app.ui.dashboard_html import DASHBOARD_HTML
from app.bot.dispatcher import set_webhook, delete_webhook, set_bot_commands, dp, bot
from app.core.database import db
from app.services.userbot import userbot_service
from app.services.scheduler import scheduler_service

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting StanlOS...")
    try:
        loop = asyncio.get_running_loop()
        asyncio.set_event_loop(loop)
    except Exception:
        pass

    await db.initialize_schema()
    await db.start_keep_alive()
    scheduler_service.start()
    await userbot_service.start()
    await set_bot_commands()
    
    polling_task = None
    if settings.WEBHOOK_URL:
        await set_webhook()
    else:
        logger.info("No WEBHOOK_URL configured. Starting long-polling...")
        polling_task = asyncio.create_task(dp.start_polling(bot, handle_signals=False))
        
    try:
        from app.utils.formatters import SYMBOLS
        for admin_id in settings.ADMIN_IDS:
            await bot.send_message(
                chat_id=admin_id, 
                text=f"{SYMBOLS['alert']} <b>StanlOS Update Deployed!</b>\n\nSystem has successfully rebooted with the latest code updates.",
                parse_mode="HTML"
            )
    except Exception as e:
        logger.error(f"Failed to send startup banner: {e}")
        
    yield
    
    logger.info("Shutting down StanlOS...")
    if polling_task:
        try:
            await dp.stop_polling()
        except Exception:
            pass
        polling_task.cancel()
    scheduler_service.stop()
    await userbot_service.stop()
    await db.stop_keep_alive()

app = FastAPI(
    title="StanlOS API",
    description="The Universal AI Assistant (StanlOS V2)",
    version="2.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(webhooks_telegram.router, tags=["Telegram"])
app.include_router(webhooks_sms.router, tags=["SMS Webhooks"])
app.include_router(webhooks_github.router, tags=["GitHub Webhooks"])
app.include_router(dashboard_api.router)

@app.get("/", response_class=HTMLResponse, tags=["Dashboard"])
async def root():
    return HTMLResponse(content=DASHBOARD_HTML)

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "alive", "system": "StanlOS"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        reload_excludes=["*.session*", "*.journal*", "*.sqlite*", "*.db*"]
    )
