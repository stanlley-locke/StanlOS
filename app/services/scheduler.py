import logging
from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger
from app.core.config import settings
from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.bot.dispatcher import bot
import feedparser

logger = logging.getLogger(__name__)

async def morning_briefing_job():
    logger.info("Executing Morning Briefing Job...")
    if not settings.ADMIN_IDS:
        return
        
    admin_id = settings.ADMIN_IDS[0]
    
    # Local import to avoid circular dependency
    from app.agent.tools import get_weather
    
    # 1. Fetch pending tasks
    tasks = await db.execute("SELECT title, due_date FROM tasks WHERE user_id = ? AND status = 'pending'", (admin_id,), fetch=True)
    task_text = "\n".join([f"- {t[0]} (Due: {t[1]})" for t in tasks]) if tasks else "No pending tasks for today."
    
    # 2. Fetch Weather
    weather = await get_weather("Nairobi")
    
    # 3. Fetch Tech/Finance News
    news_text = ""
    try:
        feed = feedparser.parse("https://feeds.bbci.co.uk/news/technology/rss.xml")
        entries = feed.entries[:3]
        news_text = "\n".join([f"- {entry.title}" for entry in entries])
    except Exception:
        news_text = "News feed unavailable."

    # 4. Generate AI Summary
    prompt = f"""
    You are StanlOS, an executive AI assistant. Create a brief, highly professional 'Morning Executive Briefing' for the user.
    Use this data:
    WEATHER: {weather}
    TASKS: {task_text}
    TOP NEWS: {news_text}
    
    Keep it concise, energizing, and well-structured using HTML for Telegram. Do not hallucinate data.
    """
    
    messages = [{"role": "system", "content": prompt}]
    briefing = await ai_client.generate_text(messages)
    
    if briefing:
        try:
            await bot.send_message(chat_id=admin_id, text=briefing)
            logger.info("Morning briefing sent successfully.")
        except Exception as e:
            logger.error(f"Failed to send morning briefing: {e}")

class TaskScheduler:
    def __init__(self):
        self.scheduler = AsyncIOScheduler(timezone="Africa/Nairobi")

    def start(self):
        # Run daily at 07:00
        self.scheduler.add_job(
            morning_briefing_job,
            trigger=CronTrigger(hour=7, minute=0),
            id='morning_briefing',
            replace_existing=True
        )
        self.scheduler.start()
        logger.info("APScheduler started successfully.")

    def stop(self):
        self.scheduler.shutdown(wait=False)

scheduler_service = TaskScheduler()
