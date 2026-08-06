import logging
import psutil
import shutil
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from app.core.config import settings
from app.core.database import db
from app.utils.formatters import SYMBOLS, build_sub_menu_kb

router = Router()
logger = logging.getLogger(__name__)

def _is_admin(user_id: int) -> bool:
    return user_id in settings.ADMIN_IDS

@router.callback_query(F.data == "menu:devops")
@router.message(Command("devops", "ec2"))
async def cmd_devops(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not _is_admin(user_id):
        text = f"{SYMBOLS['alert']} Admin access required."
        if isinstance(event, CallbackQuery):
            return await event.answer(text, show_alert=True)
        return await event.answer(text)
        
    text = (
        f"<b>SYSTEM ADMINISTRATION</b>\n"
        f""
        f"Status: {SYMBOLS['success']} ONLINE\n\n"
        "<b>Operations Available:</b>\n"
        f"{SYMBOLS['bullet']} /stats - Server resource utilization\n"
        f"{SYMBOLS['bullet']} /health - Subsystem connectivity check"
    )
    kb = build_sub_menu_kb([])
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if not _is_admin(message.from_user.id):
        return await message.answer(f"{SYMBOLS['alert']} Admin access required.")
    
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    
    text = (
        f"<b>SERVER PERFORMANCE METRICS</b>\n"
        f""
        f"CPU Usage : {cpu}%\n"
        f"RAM Used  : {ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)\n"
        f"Disk Free : {disk.free // (1024**3)}GB / {disk.total // (1024**3)}GB\n"
        f"Uptime    : {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')}\n"
    )
    await message.answer(text)

@router.message(Command("health"))
async def cmd_health(message: Message):
    if not _is_admin(message.from_user.id):
        return await message.answer(f"{SYMBOLS['alert']} Admin access required.")
    
    status_msg = await message.answer("Executing system diagnostics...")
    
    # 1. Database Check
    try:
        await db.execute("SELECT 1")
        db_status = f"{SYMBOLS['success']} Connected"
    except Exception:
        db_status = f"{SYMBOLS['alert']} Offline"
        
    # 2. Cloudflare AI Check
    try:
        from app.services.ai_cloudflare import ai_client
        res = await ai_client.generate_text([{"role": "user", "content": "ping"}])
        ai_status = f"{SYMBOLS['success']} Connected" if res else f"{SYMBOLS['alert']} Timeout"
    except Exception:
        ai_status = f"{SYMBOLS['alert']} Error"

    text = (
        f"<b>DIAGNOSTIC REPORT</b>\n"
        f""
        f"SQLite Cloud DB : {db_status}\n"
        f"Cloudflare AI   : {ai_status}\n"
    )
    await status_msg.edit_text(text)