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
    
    # Get pending tasks count
    pending_count = await db.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'",
        (user_id,), fetch=True
    )
    data["pending_tasks_count"] = pending_count[0][0] if pending_count else 0
    
    # Get finance stats
    fin = await db.execute(
        "SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'",
        (user_id,), fetch=True
    )
    if fin and fin[0][0]:
        data["finance"] = f"Total Expense: Ksh {fin[0][0]:,.2f}"
        
    # Get KB stats
    kb_count = await db.execute(
        "SELECT COUNT(*) FROM documents WHERE user_id = ?",
        (user_id,), fetch=True
    )
    data["knowledge_count"] = kb_count[0][0] if kb_count else 0
    
    # Get CRM stats
    contacts_count = await db.execute(
        "SELECT COUNT(*) FROM contacts WHERE user_id = ?",
        (user_id,), fetch=True
    )
    data["contacts_count"] = contacts_count[0][0] if contacts_count else 0
    
    # Get user gamification points
    user_info = await db.execute(
        "SELECT points FROM users WHERE tg_id = ?",
        (user_id,), fetch=True
    )
    data["points"] = user_info[0][0] if user_info and user_info[0][0] is not None else 0
        
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
        f"<b>⚙️ SYSTEM CONFIGURATION</b>\n\n"
        f"<b>Current Active Profile:</b>\n"
        f"{SYMBOLS['bullet']} <b>User ID:</b> <code>{cb.from_user.id}</code>\n"
        f"{SYMBOLS['bullet']} <b>Role:</b> {'Administrator' if cb.from_user.id in settings.ADMIN_IDS else 'Standard User'}\n"
        f"{SYMBOLS['bullet']} <b>LLM Model:</b> Llama 3.1 8B Instruct\n"
        f"{SYMBOLS['bullet']} <b>Embeddings Engine:</b> BGE Base En v1.5\n"
        f"{SYMBOLS['bullet']} <b>Database Engine:</b> SQLite Cloud\n"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]
    ])
    await cb.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "menu:help")
async def cb_help(cb: CallbackQuery):
    text = (
        f"<b>📖 STANLOS COMMAND REFERENCE</b>\n\n"
        f"<b>📚 Academic & Tasks:</b>\n"
        f"{SYMBOLS['bullet']} /tasks - View pending task list\n"
        f"{SYMBOLS['bullet']} /assign - Add new assignment/task\n\n"
        f"<b>💳 Finance & Expenses:</b>\n"
        f"{SYMBOLS['bullet']} /finance - Financial summary\n"
        f"{SYMBOLS['bullet']} /expense &lt;details&gt; - Log expense manually\n"
        f"{SYMBOLS['bullet']} /summary - View category breakdown\n\n"
        f"<b>🧠 Memory & Knowledge (RAG):</b>\n"
        f"{SYMBOLS['bullet']} /note &lt;text&gt; - Commit note to RAG database\n"
        f"{SYMBOLS['bullet']} /find &lt;query&gt; - Perform semantic vector search\n\n"
        f"<b>📇 Network Intelligence (CRM):</b>\n"
        f"{SYMBOLS['bullet']} /contact &lt;name, details&gt; - Record new contact\n"
        f"{SYMBOLS['bullet']} /network - View contact database\n\n"
        f"<b>🎬 Media & Documents:</b>\n"
        f"{SYMBOLS['bullet']} /yt &lt;url&gt; - Download audio from YouTube\n"
        f"{SYMBOLS['bullet']} <i>Send any PDF</i> - Extract text & index into RAG memory\n\n"
        f"<b>🎮 Gamification & Trivia:</b>\n"
        f"{SYMBOLS['bullet']} /trivia &lt;topic&gt; - Challenge AI quiz\n"
        f"{SYMBOLS['bullet']} /checkin - Claim daily points bonus\n\n"
        f"<b>⚙️ System Admin:</b>\n"
        f"{SYMBOLS['bullet']} /devops or /stats - View server CPU/RAM utilization\n"
        f"{SYMBOLS['bullet']} /health - Subsystem connectivity test"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]
    ])
    await cb.message.edit_text(text, reply_markup=kb)

@router.message(Command("weather"))
@router.callback_query(F.data == "menu:weather")
async def cmd_weather(event: Message | CallbackQuery):
    location = "Nairobi"
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            location = parts[1]
            
    from app.agent.tools import get_weather
    result = await get_weather(location)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    text = f"<b>🌤️ WEATHER REPORT</b>\n\n{result}\n\n<i>Type /weather &lt;city&gt; to check any location.</i>"
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "menu:calc")
@router.message(Command("calculate", "calc"))
async def cmd_calc(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            from app.agent.tools import calculate
            res = await calculate(parts[1])
            return await event.answer(f"<b>🧮 CALCULATION RESULT</b>\n\n{res}", reply_markup=kb)
            
    text = (
        f"<b>🧮 MATHEMATICAL CALCULATOR</b>\n\n"
        f"Usage: <code>/calculate &lt;expression&gt;</code>\n"
        f"Examples:\n"
        f"• <code>/calculate 1500 * 0.16 + 250</code>\n"
        f"• <code>/calculate (25000 - 1500) / 30</code>"
    )
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.message(Command("memory"))
async def cmd_memory(message: Message):
    user_id = message.from_user.id
    from app.agent.tools import recall_fact
    facts = await recall_fact(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    await message.answer(f"<b>🧠 STORED PERSONAL FACTS</b>\n\n{facts}", reply_markup=kb)
