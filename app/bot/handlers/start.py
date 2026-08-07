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

@router.message(Command("help"))
@router.callback_query(F.data == "menu:help")
async def cmd_help(event: Message | CallbackQuery):
    text = (
        f"<b>StanlOS Command Reference</b>\n\n"
        f"• <b>Tasks:</b> /tasks, /assign &lt;title&gt;, /clear_tasks\n"
        f"• <b>Finance:</b> /finance, /expense &lt;amt vendor&gt;, /income &lt;amt source&gt;, /summary, /history\n"
        f"• <b>Tools:</b> /convert 100 USD KES, /crypto BTC, /translate Swahili text, /wiki concept\n"
        f"• <b>Memory:</b> /note &lt;text&gt;, /find &lt;query&gt;, /memory\n"
        f"• <b>CRM:</b> /contact &lt;name&gt;, /network\n"
        f"• <b>Media:</b> /yt &lt;url&gt; (YouTube/TikTok), PDF upload\n"
        f"• <b>System:</b> /devops, /stats, /help"
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]
    ])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "menu:tools")
async def cb_tools(cb: CallbackQuery):
    text = (
        f"<b>Tools & Utilities Hub</b>\n\n"
        f"• <b>FX Converter:</b> <code>/convert 100 USD KES</code>\n"
        f"• <b>Crypto Market:</b> <code>/crypto BTC</code> or <code>/crypto ETH</code>\n"
        f"• <b>AI Translator:</b> <code>/translate Swahili Good morning</code>\n"
        f"• <b>Wikipedia Lookup:</b> <code>/wiki Quantum Computing</code>\n"
        f"• <b>Math Calculator:</b> <code>/calc 1500 * 0.16</code>"
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

@router.message(Command("convert"))
async def cmd_convert(message: Message):
    parts = message.text.split()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) >= 4:
        from app.agent.tools import currency_converter
        amt = parts[1]
        fc = parts[2]
        tc = parts[3]
        res = await currency_converter(amt, fc, tc)
        await message.answer(f"<b>CURRENCY CONVERTER</b>\n\n{res}", reply_markup=kb)
    else:
        await message.answer(
            "<b>CURRENCY CONVERTER</b>\n\nUsage: <code>/convert &lt;amount&gt; &lt;from&gt; &lt;to&gt;</code>\nExample: <code>/convert 100 USD KES</code>",
            reply_markup=kb
        )

@router.message(Command("crypto"))
async def cmd_crypto(message: Message):
    parts = message.text.split()
    sym = parts[1] if len(parts) > 1 else "BTC"
    from app.agent.tools import crypto_tracker
    res = await crypto_tracker(sym)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    await message.answer(f"<b>CRYPTO MARKET LOOKUP</b>\n\n{res}", reply_markup=kb)

@router.message(Command("translate"))
async def cmd_translate(message: Message):
    parts = message.text.split(maxsplit=2)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) >= 3:
        target_lang = parts[1]
        text_to_translate = parts[2]
        from app.agent.tools import translate_text
        res = await translate_text(text_to_translate, target_lang)
        await message.answer(f"<b>AI TRANSLATOR ({target_lang.upper()})</b>\n\n{res}", reply_markup=kb)
    else:
        await message.answer(
            "<b>AI TRANSLATOR</b>\n\nUsage: <code>/translate &lt;language&gt; &lt;text&gt;</code>\nExample: <code>/translate Swahili Good morning friend</code>",
            reply_markup=kb
        )

@router.message(Command("wiki"))
async def cmd_wiki(message: Message):
    parts = message.text.split(maxsplit=1)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) > 1:
        from app.agent.tools import wiki_search
        res = await wiki_search(parts[1])
        await message.answer(f"<b>WIKIPEDIA SEARCH</b>\n\n{res}", reply_markup=kb)
    else:
        await message.answer(
            "<b>WIKIPEDIA SEARCH</b>\n\nUsage: <code>/wiki &lt;concept&gt;</code>\nExample: <code>/wiki Artificial Intelligence</code>",
            reply_markup=kb
        )

@router.message(Command("clear_tasks"))
async def cmd_clear_tasks(message: Message):
    user_id = message.from_user.id
    from app.agent.tools import clear_tasks
    res = await clear_tasks(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    await message.answer(f"<b>TASK LIST WIPED</b>\n\n{res}", reply_markup=kb)
