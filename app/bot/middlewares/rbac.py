from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery, TelegramObject
from typing import Callable, Dict, Any, Awaitable
from app.core.database import db
from app.utils.formatters import SYMBOLS

SENSITIVE_COMMANDS = [
    "/finance", "/expense", "/income", "/summary", "/history", 
    "/devops", "/shell", "/stats", "/invite_admin", "/demote", "/list_admins"
]
SENSITIVE_CALLBACKS = ["menu:finance", "menu:devops", "menu:settings", "finance:", "devops:"]

class RBACMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[TelegramObject, Dict[str, Any]], Awaitable[Any]],
        event: TelegramObject,
        data: Dict[str, Any]
    ) -> Any:
        
        user_id = None
        text_or_data = ""
        is_callback = False
        
        if isinstance(event, Message):
            user_id = event.from_user.id
            text_or_data = event.text or ""
        elif isinstance(event, CallbackQuery):
            user_id = event.from_user.id
            text_or_data = event.data or ""
            is_callback = True
            
        if user_id:
            is_sensitive = False
            if is_callback:
                if any(text_or_data.startswith(sc) for sc in SENSITIVE_CALLBACKS):
                    is_sensitive = True
            else:
                if any(text_or_data.startswith(sc) for sc in SENSITIVE_COMMANDS):
                    is_sensitive = True
                    
            if is_sensitive:
                rows = await db.execute("SELECT role FROM users WHERE tg_id = ?", (user_id,), fetch=True)
                role = rows[0][0] if rows else 'guest'
                
                if role != 'admin':
                    msg = f"⛔ <b>Access Denied</b>\n\nThis system module requires Administrator privileges. Your current role is: <code>{role.upper()}</code>."
                    if isinstance(event, Message):
                        await event.answer(msg)
                    elif isinstance(event, CallbackQuery):
                        await event.answer("Access Denied: Admin required.", show_alert=True)
                    return # Block handler propagation
                    
        return await handler(event, data)
