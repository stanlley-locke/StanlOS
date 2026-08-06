import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core.config import settings
from app.api import webhooks_telegram, webhooks_sms
from app.bot.dispatcher import set_webhook, delete_webhook, dp, bot
from app.core.database import db
from app.services.userbot import userbot_service

logging.basicConfig(
    level=settings.LOG_LEVEL,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

import asyncio

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Starting StanlOS...")
    await db.initialize_schema()
    await userbot_service.start()
    
    if settings.WEBHOOK_URL:
        await set_webhook()
    else:
        logger.info("No WEBHOOK_URL configured. Starting long-polling...")
        asyncio.create_task(dp.start_polling(bot))
        
    yield
    
    logger.info("Shutting down StanlOS...")
    await delete_webhook()
    await userbot_service.stop()

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

@app.get("/health", tags=["System"])
async def health_check():
    return {"status": "alive", "system": "StanlOS"}
