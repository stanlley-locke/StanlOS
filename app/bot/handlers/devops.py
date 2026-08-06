import logging
import psutil
import shutil
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from app.core.config import settings
from app.core.database import db
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, make_progress_bar

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
        f"<b>{SYMBOLS['devops']} SYSTEM ADMINISTRATION & DEVOPS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>System Status:</b> {SYMBOLS['success']} ONLINE\n\n"
        f"<b>Available Operations:</b>\n"
        f"{SYMBOLS['bullet']} /stats - Server resource utilization gauges\n"
        f"{SYMBOLS['bullet']} /health - Subsystem connectivity test"
    )
    buttons = [
        [("📊 Resource Metrics", "devops:stats"), ("🔍 Health Diagnostics", "devops:health")]
    ]
    kb = build_sub_menu_kb(buttons)
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "devops:stats")
@router.message(Command("stats"))
async def cmd_stats(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not _is_admin(user_id):
        text = f"{SYMBOLS['alert']} Admin access required."
        if isinstance(event, CallbackQuery):
            return await event.answer(text, show_alert=True)
        return await event.answer(text)
    
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    disk_pct = ((disk.total - disk.free) / disk.total) * 100
    
    cpu_bar = make_progress_bar(cpu, length=10)
    ram_bar = make_progress_bar(ram.percent, length=10)
    disk_bar = make_progress_bar(disk_pct, length=10)
    
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')
    
    text = (
        f"<b>📊 SERVER PERFORMANCE METRICS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>CPU Usage:</b> {cpu_bar}\n"
        f"<b>RAM Usage:</b> {ram_bar}\n"
        f"  └ Used: {ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB\n\n"
        f"<b>Disk Space:</b> {disk_bar}\n"
        f"  └ Free: {disk.free // (1024**3)}GB / {disk.total // (1024**3)}GB\n\n"
        f"<b>Server Uptime:</b> <code>{uptime}</code>"
    )
    kb = build_sub_menu_kb([])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "devops:health")
@router.message(Command("health"))
async def cmd_health(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not _is_admin(user_id):
        text = f"{SYMBOLS['alert']} Admin access required."
        if isinstance(event, CallbackQuery):
            return await event.answer(text, show_alert=True)
        return await event.answer(text)
    
    msg_target = event if isinstance(event, Message) else event.message
    status_msg = await msg_target.answer(f"{SYMBOLS['ai']} Running subsystem diagnostics...")
    
    # 1. Database Check
    try:
        await db.execute("SELECT 1")
        db_status = f"{SYMBOLS['success']} Connected (SQLite Cloud)"
    except Exception as e:
        db_status = f"{SYMBOLS['alert']} Offline ({e})"
        
    # 2. Cloudflare AI Check
    try:
        from app.services.ai_cloudflare import ai_client
        res = await ai_client.generate_text([{"role": "user", "content": "ping"}])
        ai_status = f"{SYMBOLS['success']} Operational (Llama 3.1 8B)" if res else f"{SYMBOLS['alert']} Timeout"
    except Exception as e:
        ai_status = f"{SYMBOLS['alert']} Error ({e})"

    # 3. Userbot Check
    from app.services.userbot import userbot_service
    userbot_status = f"{SYMBOLS['success']} Connected" if userbot_service.is_running else f"{SYMBOLS['alert']} Stopped"

    text = (
        f"<b>🔍 DIAGNOSTIC REPORT</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"<b>SQLite Cloud DB :</b> {db_status}\n"
        f"<b>Cloudflare AI   :</b> {ai_status}\n"
        f"<b>Pyrogram Userbot :</b> {userbot_status}\n"
        f"<b>Overall Status   :</b> {SYMBOLS['success']} SYSTEM HEALTHY"
    )
    kb = build_sub_menu_kb([])
    await status_msg.edit_text(text, reply_markup=kb)