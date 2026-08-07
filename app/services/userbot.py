import logging
import asyncio
from pyrogram import Client
from typing import List, Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class UserbotService:
    def __init__(self):
        self.app: Client = None
        self.is_running = False

    async def start(self):
        if not settings.API_ID or not settings.API_HASH:
            logger.warning("Userbot not started: API_ID or API_HASH missing.")
            return

        if settings.PYROGRAM_SESSION_STRING:
            self.app = Client(
                "my_account",
                api_id=settings.API_ID,
                api_hash=settings.API_HASH,
                session_string=settings.PYROGRAM_SESSION_STRING,
                no_updates=True
            )
        else:
            self.app = Client(
                "my_account",
                api_id=settings.API_ID,
                api_hash=settings.API_HASH,
                phone_number=settings.PHONE_NUMBER,
                no_updates=True
            )
        
        try:
            await self.app.start()
            self.is_running = True
            me = await self.app.get_me()
            logger.info(f"Pyrogram Userbot started successfully as: {me.first_name} (@{me.username}) | ID: {me.id} | is_bot: {me.is_bot}")
        except Exception as e:
            logger.error(f"Failed to start Userbot: {e}")
            logger.info("Did you run 'python auth_userbot.py' first?")
            self.is_running = False

    async def stop(self):
        if self.is_running and self.app:
            try:
                await self.app.stop()
            except Exception as e:
                logger.error(f"Error stopping Userbot: {e}")
            finally:
                self.is_running = False
                logger.info("Pyrogram Userbot stopped.")

    async def send_message(self, chat_id: str | int, text: str) -> str:
        """Send a message as the user."""
        if not self.is_running:
            return "Error: Userbot is not running."
        try:
            if isinstance(chat_id, str):
                chat_id = chat_id.strip("'\" ")
                if chat_id.startswith("@") or chat_id.startswith("+"):
                    try:
                        await self.app.get_chat(chat_id)
                    except Exception:
                        pass
            await self.app.send_message(chat_id, text)
            return f"Message sent to {chat_id} successfully."
        except Exception as e:
            logger.error(f"Userbot send_message error: {e}")
            return f"Failed to send message: {e}"

    async def get_history(self, chat_id: str | int, limit: int | str = 5) -> str:
        """Fetch recent messages from a chat."""
        if not self.is_running:
            return "Error: Userbot is not running."
        try:
            limit_int = int(limit) if str(limit).isdigit() else 5
            if isinstance(chat_id, str):
                chat_id = chat_id.strip("'\" ")
                if chat_id.startswith("@") or chat_id.startswith("+"):
                    try:
                        await self.app.get_chat(chat_id)
                    except Exception:
                        pass
            messages = []
            async for msg in self.app.get_chat_history(chat_id, limit=limit_int):
                sender = msg.from_user.first_name if msg.from_user else "Unknown"
                text = msg.text or "[Media]"
                messages.append(f"{sender}: {text}")
            
            # Reverse so chronological
            messages.reverse()
            return "\n".join(messages) if messages else "No history found."
        except Exception as e:
            logger.error(f"Userbot get_history error: {e}")
            return f"Failed to fetch history: {e}"

userbot_service = UserbotService()
