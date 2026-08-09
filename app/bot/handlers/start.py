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
    
    # Investments Data
    import aiohttp
    data["total_worth"] = 0.0
    data["stock_data"] = {}
    
    mmf_rows = await db.execute("SELECT current_balance FROM investments_mmf WHERE user_id = ?", (user_id,), fetch=True)
    if mmf_rows:
        for r in mmf_rows:
            data["total_worth"] += float(r[0])
            
    stock_rows = await db.execute("SELECT ticker, shares FROM investments_stocks WHERE user_id = ?", (user_id,), fetch=True)
    if stock_rows:
        tickers_query = []
        shares_map = {}
        for r in stock_rows:
            sym = r[0]
            shares = float(r[1])
            tickers_query.append(f"NSEKE:{sym}")
            shares_map[sym] = shares
            
        url = "https://scanner.tradingview.com/kenya/scan"
        payload = {"symbols": {"tickers": tickers_query}, "columns": ["close"]}
        try:
            async with aiohttp.ClientSession(headers={"User-Agent": "Mozilla/5.0"}) as session:
                async with session.post(url, json=payload, timeout=3) as resp:
                    if resp.status == 200:
                        td = await resp.json()
                        if td.get("data"):
                            for item in td["data"]:
                                sym = item["s"].replace("NSEKE:", "")
                                price = float(item["d"][0] if item["d"] else 0.0)
                                shares = shares_map.get(sym, 0)
                                val = price * shares
                                data["total_worth"] += val
                                data["stock_data"][sym] = val
        except Exception as e:
            logger.error(f"Failed to fetch stock prices for dashboard: {e}")
            
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
    chart_file = generate_dashboard_chart(data["total_income"], data["total_expense"], data.get("stock_data"), data.get("total_worth", 0.0))
    
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
        f"• <b>Finance:</b> /finance, /expense, /income, /summary\n"
        f"• <b>Investments:</b> /investments, /update_mmf, /buy_stock\n"
        f"• <b>Tools:</b> /convert 100 USD KES, /unit 10 km mi, /time, /qr &lt;url&gt;\n"
        f"• <b>Markets:</b> /stock TSLA, /nse SCOM, /crypto BTC\n"
        f"• <b>Research:</b> /wiki concept, /github python, /summarize &lt;text&gt;\n"
        f"• <b>Memory:</b> /note &lt;text&gt;, /find &lt;query&gt;, /memory\n"
        f"• <b>CRM & Media:</b> /contact &lt;name&gt;, /yt &lt;url&gt;\n"
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
        f"<b>Tools, Forecasts & Live Information</b>\n\n"
        f"• <b>Weather:</b> <code>/weather Nairobi</code>\n"
        f"• <b>Stocks (US):</b> <code>/stock TSLA</code>\n"
        f"• <b>Stocks (NSE):</b> <code>/nse SCOM</code>\n"
        f"• <b>Crypto:</b> <code>/crypto BTC</code>\n"
        f"• <b>Currency Convert:</b> <code>/convert 100 USD KES</code>\n"
        f"• <b>Unit Convert:</b> <code>/unit 10 km mi</code>\n"
        f"• <b>Time:</b> <code>/time</code>\n"
        f"• <b>Wikipedia:</b> <code>/wiki Quantum Computing</code>\n"
        f"• <b>QR Code:</b> <code>/qr https://google.com</code>\n"
        f"• <b>GitHub:</b> <code>/github python</code>\n"
        f"• <b>Summarize:</b> <code>/summarize [long text]</code>"
    )
    buttons = [
        [("Top Market Movers", "menu:market_movers")],
        [("Check Weather", "menu:weather"), ("Check Crypto", "menu:crypto_quick")],
        [("US Stocks", "menu:stock_quick"), ("NSE Kenya Stocks", "menu:nse_quick")],
        [("Convert Currency", "menu:convert_quick"), ("Convert Unit", "menu:unit_quick")],
        [("Check Time", "menu:time_quick"), ("Wikipedia Search", "menu:wiki_quick")],
        [("Generate QR Code", "menu:qr_quick"), ("GitHub Trending", "menu:github_quick")]
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

@router.message(Command("time"))
@router.callback_query(F.data == "menu:time_quick")
async def cmd_time(event: Message | CallbackQuery):
    from app.agent.tools import get_current_time
    res = await get_current_time()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    text = f"<b>🕒 CURRENT TIME</b>\n\n{res}"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("unit"))
@router.callback_query(F.data == "menu:unit_quick")
async def cmd_unit(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split()
        if len(parts) >= 4:
            from app.agent.tools import unit_converter
            res = await unit_converter(parts[1], parts[2], parts[3])
            return await event.answer(f"<b>📏 UNIT CONVERTER</b>\n\n{res}", reply_markup=kb)
            
    text = "<b>📏 UNIT CONVERTER</b>\n\nUsage: <code>/unit &lt;value&gt; &lt;from&gt; &lt;to&gt;</code>\nExample: <code>/unit 10 km mi</code>"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("qr"))
@router.callback_query(F.data == "menu:qr_quick")
async def cmd_qr(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            from app.agent.tools import generate_qr_code
            await generate_qr_code(event.from_user.id, parts[1])
            return
            
    text = "<b>⬛ QR GENERATOR</b>\n\nUsage: <code>/qr &lt;data_or_url&gt;</code>\nExample: <code>/qr https://google.com</code>"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("stock"))
@router.callback_query(F.data == "menu:stock_quick")
async def cmd_stock(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            from app.agent.tools import get_stock_price
            res = await get_stock_price(parts[1])
            return await event.answer(f"<b>📈 US STOCK MARKET</b>\n\n{res}", reply_markup=kb)
            
    text = "<b>📈 US STOCK MARKET</b>\n\nUsage: <code>/stock &lt;ticker&gt;</code>\nExample: <code>/stock TSLA</code>"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("nse"))
@router.callback_query(F.data == "menu:nse_quick")
async def cmd_nse(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        if len(parts) > 1:
            from app.agent.tools import get_nse_stock_price
            res = await get_nse_stock_price(parts[1])
            return await event.answer(f"<b>🇰🇪 NSE KENYA MARKET</b>\n\n{res}", reply_markup=kb)
            
    text = "<b>🇰🇪 NSE KENYA MARKET</b>\n\nUsage: <code>/nse &lt;ticker&gt;</code>\nExample: <code>/nse SCOM</code>"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("github"))
@router.callback_query(F.data == "menu:github_quick")
async def cmd_github(event: Message | CallbackQuery):
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if isinstance(event, Message):
        parts = event.text.split(maxsplit=1)
        lang = parts[1] if len(parts) > 1 else "python"
        from app.agent.tools import fetch_github_trending
        res = await fetch_github_trending(lang)
        return await event.answer(f"<b>🐙 GITHUB TRENDING ({lang})</b>\n\n{res}", reply_markup=kb)
        
    text = "<b>🐙 GITHUB TRENDING</b>\n\nUsage: <code>/github &lt;language&gt;</code>\nExample: <code>/github python</code>\nExample: <code>/github javascript</code>"
    await smart_edit(event, text, reply_markup=kb)

@router.message(Command("summarize"))
async def cmd_summarize(message: Message):
    parts = message.text.split(maxsplit=1)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) > 1:
        from app.agent.tools import summarize_text
        status = await message.answer("Summarizing...")
        res = await summarize_text(parts[1])
        await status.edit_text(f"<b>📝 TEXT SUMMARY</b>\n\n{res}", reply_markup=kb)
        await message.answer("<b>📝 TEXT SUMMARY</b>\n\nUsage: <code>/summarize &lt;long text&gt;</code>", reply_markup=kb)

@router.callback_query(F.data == "menu:market_movers")
async def cb_market_movers(cb: CallbackQuery):
    from app.agent.tools import analyze_market_opportunities
    status = await cb.message.answer(f"{SYMBOLS['ai']} Analyzing live NSE market movers...")
    res = await analyze_market_opportunities()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Forecasts", callback_data="menu:forecasts")]])
    await smart_edit(status, res, reply_markup=kb)

@router.message(Command("investments"))
@router.callback_query(F.data == "menu:investments")
async def cmd_investments(event: Message | CallbackQuery):
    user_id = event.from_user.id
    from app.agent.tools import get_investment_portfolio
    if isinstance(event, Message):
        status = await event.answer(f"{SYMBOLS['ai']} Fetching live market data...")
    else:
        status = await event.message.answer(f"{SYMBOLS['ai']} Fetching live market data...")
        
    res = await get_investment_portfolio(user_id)
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
    await smart_edit(status, res, reply_markup=kb)

@router.message(Command("buy_stock", "sell_stock", "update_stock"))
async def cmd_update_stock(message: Message):
    parts = message.text.split()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) >= 3:
        try:
            ticker = parts[1]
            shares = float(parts[2])
            from app.agent.tools import update_stock_shares
            res = await update_stock_shares(message.from_user.id, ticker, shares)
            await message.answer(f"<b>📈 PORTFOLIO UPDATED</b>\n\n{res}", reply_markup=kb)
        except ValueError:
            await message.answer("Shares must be a number.", reply_markup=kb)
    else:
        await message.answer(
            "<b>📈 UPDATE PORTFOLIO</b>\n\nUsage: <code>/update_stock &lt;ticker&gt; &lt;total_shares&gt;</code>\nExample: <code>/update_stock SCOM 100</code>\n"
            "(To sell/remove a stock completely, set shares to 0)",
            reply_markup=kb
        )

@router.message(Command("update_mmf"))
async def cmd_update_mmf(message: Message):
    # /update_mmf CMMF 87340 11.11
    parts = message.text.split()
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
    if len(parts) >= 4:
        try:
            fund_name = parts[1]
            balance = float(parts[2])
            yield_pct = float(parts[3])
            from app.agent.tools import update_mmf_balance
            res = await update_mmf_balance(message.from_user.id, fund_name, balance, yield_pct)
            await message.answer(f"<b>🏦 MMF UPDATED</b>\n\n{res}", reply_markup=kb)
        except ValueError:
            await message.answer("Balance and yield must be numbers.", reply_markup=kb)
    else:
        await message.answer(
            "<b>🏦 UPDATE MMF</b>\n\nUsage: <code>/update_mmf &lt;FundName&gt; &lt;Balance&gt; &lt;Yield%&gt;</code>\nExample: <code>/update_mmf CMMF 87340 11.11</code>",
            reply_markup=kb
        )
