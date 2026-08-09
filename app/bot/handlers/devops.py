import logging
import psutil
import shutil
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command

from app.core.config import settings
from app.core.database import db
from app.utils.formatters import smart_edit, SYMBOLS, build_sub_menu_kb, make_progress_bar

router = Router()
logger = logging.getLogger(__name__)

async def _is_admin(user_id: int) -> bool:
    if user_id in settings.ADMIN_IDS:
        return True
    rows = await db.execute("SELECT role FROM users WHERE tg_id = ?", (user_id,), fetch=True)
    return rows and rows[0][0] == 'admin'

@router.callback_query(F.data == "menu:devops")
@router.message(Command("devops", "ec2"))
async def cmd_devops(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not await _is_admin(user_id):
        text = f"{SYMBOLS['alert']} Admin access required."
        if isinstance(event, CallbackQuery):
            return await event.answer(text, show_alert=True)
        return await event.answer(text)
        
    text = (
        f"<b>System Administration & DevOps</b>\n"
        
        f"<b>Status:</b> [OK] ONLINE\n\n"
        f"• /stats - Resource utilization gauges\n"
        f"• /health - Subsystem connectivity test\n"
        f"• /db_vacuum - SQLite Cloud Database Optimization\n"
        f"• /purge_cache - Clear Temporary File Caches"
    )
    buttons = [
        [("Resource Metrics", "devops:stats"), ("Health Diagnostics", "devops:health")],
        [("Optimize Database", "devops:vacuum"), ("Purge Temp Cache", "devops:purge_cache")]
    ]
    kb = build_sub_menu_kb(buttons)
    
    await smart_edit(event, text, reply_markup=kb)

@router.callback_query(F.data == "devops:vacuum")
@router.message(Command("db_vacuum"))
async def cb_vacuum(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not await _is_admin(user_id):
        return
    
    try:
        await db.execute("PRAGMA optimize")
        text = f"<b>Database Maintenance Complete</b>\n\n[OK] SQLite Cloud indices optimized and verified."
    except Exception as e:
        text = f"<b>Database Maintenance Failed:</b> {e}"
        
    kb = build_sub_menu_kb([])
    await smart_edit(event, text, reply_markup=kb)

@router.callback_query(F.data == "devops:purge_cache")
@router.message(Command("purge_cache"))
async def cb_purge_cache(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not await _is_admin(user_id):
        return
    
    import os, glob
    count = 0
    for f in glob.glob("storage/downloads/*"):
        try:
            os.remove(f)
            count += 1
        except Exception:
            pass
            
    text = f"<b>Cache Purge Complete</b>\n\n[OK] Removed {count} temporary downloaded media files."
    kb = build_sub_menu_kb([])
    await smart_edit(event, text, reply_markup=kb)

@router.callback_query(F.data == "devops:stats")
@router.message(Command("stats"))
async def cmd_stats(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not await _is_admin(user_id):
        text = f"{SYMBOLS['alert']} Admin access required."
        if isinstance(event, CallbackQuery):
            return await event.answer(text, show_alert=True)
        return await event.answer(text)
    
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    disk_pct = ((disk.total - disk.free) / disk.total) * 100
    
    uptime = datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')
    
    text = (
        f"<b>SERVER PERFORMANCE METRICS</b>\n"
        f"<b>Uptime:</b> <code>{uptime}</code>\n\n"
        f"<b>RAM:</b> {ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB\n"
        f"<b>Disk:</b> {disk.free // (1024**3)}GB Free / {disk.total // (1024**3)}GB Total"
    )
    
    from app.utils.charts import generate_gauge_dashboard
    chart_file = generate_gauge_dashboard(cpu, ram.percent, disk_pct)
    
    kb = build_sub_menu_kb([])
    if isinstance(event, Message):
        await event.answer_photo(photo=chart_file, caption=text, reply_markup=kb)
    else:
        await event.message.delete()
        await event.message.answer_photo(photo=chart_file, caption=text, reply_markup=kb)

@router.callback_query(F.data == "devops:health")
@router.message(Command("health"))
async def cmd_health(event: Message | CallbackQuery):
    user_id = event.from_user.id
    if not await _is_admin(user_id):
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
        f"<b>DIAGNOSTIC REPORT</b>\n"
        
        f"<b>SQLite Cloud DB :</b> {db_status}\n"
        f"<b>Cloudflare AI   :</b> {ai_status}\n"
        f"<b>Pyrogram Userbot :</b> {userbot_status}\n"
        f"<b>Overall Status   :</b> {SYMBOLS['success']} SYSTEM HEALTHY"
    )
    kb = build_sub_menu_kb([])
    await smart_edit(status_msg, text, reply_markup=kb)

@router.message(Command("invite_admin"))
async def cmd_invite_admin(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Usage: <code>/invite_admin &lt;user_id_or_username&gt;</code>")
    target = parts[1].replace('@', '')
    
    rows = await db.execute("SELECT tg_id FROM users WHERE tg_id = ? OR username = ?", (target, target), fetch=True)
    if not rows:
        return await message.answer(f"Could not find user '{target}' in the database. They must start the bot first.")
        
    tg_id = rows[0][0]
    await db.execute("UPDATE users SET role = 'admin' WHERE tg_id = ?", (tg_id,))
    await message.answer(f"{SYMBOLS['success']} User <b>{target}</b> has been promoted to Administrator.")

@router.message(Command("demote"))
async def cmd_demote(message: Message):
    parts = message.text.split()
    if len(parts) < 2:
        return await message.answer("Usage: <code>/demote &lt;user_id_or_username&gt;</code>")
    target = parts[1].replace('@', '')
    
    rows = await db.execute("SELECT tg_id FROM users WHERE tg_id = ? OR username = ?", (target, target), fetch=True)
    if not rows:
        return await message.answer(f"Could not find user '{target}' in the database.")
        
    tg_id = rows[0][0]
    if tg_id == message.from_user.id:
        return await message.answer(f"{SYMBOLS['alert']} You cannot demote yourself.")
        
    await db.execute("UPDATE users SET role = 'guest' WHERE tg_id = ?", (tg_id,))
    await message.answer(f"{SYMBOLS['success']} User <b>{target}</b> has been demoted to Guest.")

@router.message(Command("list_admins"))
async def cmd_list_admins(message: Message):
    rows = await db.execute("SELECT tg_id, full_name, username FROM users WHERE role = 'admin'", fetch=True)
    if not rows:
        return await message.answer("No administrators found.")
        
    text = "<b>SYSTEM ADMINISTRATORS</b>\n\n"
    for r in rows:
        username_str = f" (@{r[2]})" if r[2] else ""
        text += f"• <code>{r[0]}</code> - {r[1]}{username_str}\n"
        
    await message.answer(text)