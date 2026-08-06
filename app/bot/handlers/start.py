import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from app.core.database import db
from app.utils.formatters import format_dashboard, build_main_menu_kb, SYMBOLS

router = Router()
logger = logging.getLogger(__name__)

async def get_dashboard_data(user_id: int) -> dict:
    data = {}
    
    # Get academic stats
    pending_tasks = await db.execute(
        "SELECT title, due_date FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC LIMIT 1",
        (user_id,), fetch=True
    )
    if pending_tasks:
        data["academic"] = f"Next: {pending_tasks[0][0]} (Due: {pending_tasks[0][1]})"
    
    # Get finance stats (sum of current month)
    # Simple proxy for now
    fin = await db.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'",
        (user_id,), fetch=True
    )
    if fin and fin[0][0]:
        data["finance"] = f"Total Exp: {fin[0][0]}"
        
    # Get KB stats
    kb_count = await db.execute(
        "SELECT COUNT(*) FROM documents WHERE user_id = ?",
        (user_id,), fetch=True
    )
    if kb_count:
        data["knowledge_count"] = kb_count[0][0]
        
    return data

@router.message(Command("start", "menu"))
@router.callback_query(F.data == "menu:main")
async def cmd_start(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    # Ensure user exists in db
    if isinstance(event, Message):
        await db.execute(
            "INSERT OR IGNORE INTO users (tg_id, full_name, username) VALUES (?, ?, ?)",
            (user_id, event.from_user.full_name, event.from_user.username)
        )
    
    is_admin = user_id in settings.ADMIN_IDS
    data = await get_dashboard_data(user_id)
    text = format_dashboard(data)
    kb = build_main_menu_kb(is_admin)
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "menu:settings")
async def cb_settings(cb: CallbackQuery):
    text = (
        f"<b>SYSTEM SETTINGS</b>\n"
        f"\n"
        f"Data management options will be placed here."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")]
    ])
    await cb.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "menu:help")
async def cb_help(cb: CallbackQuery):
    text = (
        f"<b>SYSTEM DOCUMENTATION</b>\n"
        f"\n"
        f"{SYMBOLS['bullet']} /note &lt;text&gt; - Save note\n"
        f"{SYMBOLS['bullet']} /find &lt;query&gt; - Search knowledge\n"
        f"{SYMBOLS['bullet']} /assign - Add task\n"
        f"{SYMBOLS['bullet']} /tasks - View tasks\n"
        f"{SYMBOLS['bullet']} /trivia - Play trivia\n"
        f"{SYMBOLS['bullet']} /devops - System stats"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")]
    ])
    await cb.message.edit_text(text, reply_markup=kb)
