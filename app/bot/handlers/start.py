import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext

from app.core.config import settings
from app.core.database import db
from app.utils.formatters import format_dashboard, build_main_menu_kb, SYMBOLS, build_sub_menu_kb, smart_edit

router = Router()
logger = logging.getLogger(__name__)

async def get_dashboard_data(user_id: int) -> dict:
    data = {}
    
    # Financial Stats
    inc_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (user_id,), fetch=True)
    exp_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (user_id,), fetch=True)
    
    data["total_income"] = inc_res[0][0] or 0.0 if inc_res else 0.0
    data["total_expense"] = exp_res[0][0] or 0.0 if exp_res else 0.0
    
    top_cat_row = await db.execute(
        "SELECT category, SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense' GROUP BY category ORDER BY SUM(amount) DESC LIMIT 1",
        (user_id,), fetch=True
    )
    if top_cat_row and top_cat_row[0][0]:
        data["top_category"] = top_cat_row[0][0]
        data["top_cat_amount"] = top_cat_row[0][1] or 0.0
    else:
        data["top_category"] = "None"
        data["top_cat_amount"] = 0.0
        
    # Pending tasks count
    pending_count = await db.execute(
        "SELECT COUNT(*) FROM tasks WHERE user_id = ? AND status = 'pending'",
        (user_id,), fetch=True
    )
    data["pending_tasks_count"] = pending_count[0][0] if pending_count else 0
    
    # KB & CRM stats
    kb_count = await db.execute("SELECT COUNT(*) FROM documents WHERE user_id = ?", (user_id,), fetch=True)
    data["knowledge_count"] = kb_count[0][0] if kb_count else 0
    
    contacts_count = await db.execute("SELECT COUNT(*) FROM contacts WHERE user_id = ?", (user_id,), fetch=True)
    data["contacts_count"] = contacts_count[0][0] if contacts_count else 0
        
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
    
    from app.utils.charts import generate_dashboard_chart
    chart_file = generate_dashboard_chart(data["total_income"], data["total_expense"])
    
    if isinstance(event, Message):
        await event.answer_photo(photo=chart_file, caption=text, reply_markup=kb)
    else:
        await event.message.delete()
        await event.message.answer_photo(photo=chart_file, caption=text, reply_markup=kb)

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
    await smart_edit(cb, text, reply_markup=kb)

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
    await smart_edit(event, text, reply_markup=kb)

@router.callback_query(F.data == "menu:workload")
async def cb_workload(cb: CallbackQuery):
    user_id = cb.from_user.id
    try:
        rows = await db.execute("SELECT id, title, due_date FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC", (user_id,), fetch=True)
        if not rows:
            tasks_text = "No pending tasks."
        else:
            tasks_text = "\n".join([f"• #{r[0]}: {r[1]} (Due: {r[2]})" for r in rows])
    except Exception as e:
        tasks_text = f"Error fetching tasks: {e}"
    text = (
        f"<b>Workload & Task Management</b>\n\n"
        f"<b>Current Tasks:</b>\n{tasks_text}\n\n"
        f"• <code>/assign &lt;task title&gt;</code> - Create new task\n"
        f"• <code>/clear_tasks</code> - Delete all tasks"
    )
    buttons = [
        [("View Pending Tasks", "academic:list"), ("Add New Task", "academic:add")],
        [("Clear All Tasks", "academic:clear")]
    ]
    kb = build_sub_menu_kb(buttons)
    await smart_edit(cb, text, reply_markup=kb)

@router.callback_query(F.data == "menu:forecasts")
async def cb_forecasts(cb: CallbackQuery):
    text = (
        f"<b>Forecasts & Live Information</b>\n\n"
        f"• <b>Weather Forecast:</b> <code>/weather Nairobi</code>\n"
        f"• <b>Crypto Market Prices:</b> <code>/crypto BTC</code>\n"
        f"• <b>Currency Exchange:</b> <code>/convert 100 USD KES</code>\n"
        f"• <b>Wikipedia Lookup:</b> <code>/wiki Quantum Computing</code>"
    )
    buttons = [
        [("Check Weather", "menu:weather"), ("Check Crypto", "menu:crypto_quick")],
        [("Convert Currency", "menu:convert_quick"), ("Wikipedia Search", "menu:wiki_quick")]
    ]
    kb = build_sub_menu_kb(buttons)
    await smart_edit(cb, text, reply_markup=kb)

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
    await smart_edit(event, text, reply_markup=kb)

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
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("memory"))
async def cmd_memory(message: Message):
    user_id = message.from_user.id
    from app.agent.tools import recall_fact
    facts = await recall_fact(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    await message.answer(f"<b>STORED PERSONAL FACTS</b>\n\n{facts}", reply_markup=kb)

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
