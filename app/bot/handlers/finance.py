import logging
import json
import re
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, make_progress_bar, safe_html

router = Router()
logger = logging.getLogger(__name__)

class ExpenseState(StatesGroup):
    details = State()

class IncomeState(StatesGroup):
    details = State()

@router.callback_query(F.data == "menu:finance")
@router.message(Command("finance"))
async def cb_finance_menu(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    inc_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (user_id,), fetch=True)
    exp_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (user_id,), fetch=True)
    
    total_inc = inc_res[0][0] or 0.0 if inc_res else 0.0
    total_exp = exp_res[0][0] or 0.0 if exp_res else 0.0
    net_bal = total_inc - total_exp
    
    text = (
        f"<b>Financial Control & Accounting</b>\n\n"
        f"<b>Net Balance:</b> Ksh {net_bal:,.2f}\n"
        f"<b>Total Income:</b> +Ksh {total_inc:,.2f}\n"
        f"<b>Total Expense:</b> -Ksh {total_exp:,.2f}\n\n"
        f"• <code>/expense &lt;amount vendor&gt;</code> - Log expense\n"
        f"• <code>/income &lt;amount source&gt;</code> - Log income\n"
        f"• <code>/summary</code> - Category breakdown report\n"
        f"• <code>/history</code> - Transaction history & delete"
    )
    buttons = [
        [("Log Expense", "fin:action_expense"), ("Log Income", "fin:action_income")],
        [("Category Breakdown", "fin:summary"), ("Spending Trends", "fin:trends")],
        [("Transaction History", "fin:history"), ("Top Vendors", "fin:vendors")],
        [("Reset Financial Data", "fin:reset_confirm")]
    ]
    kb = build_sub_menu_kb(buttons)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "fin:action_expense")
async def cb_action_expense(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        f"<b>📉 LOG EXPENSE</b>\n\n"
        f"Please reply with your expense details (e.g. <i>'1500 for groceries at Carrefour'</i>):"
    )
    await state.set_state(ExpenseState.details)

@router.callback_query(F.data == "fin:action_income")
async def cb_action_income(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        f"<b>📈 LOG INCOME</b>\n\n"
        f"Please reply with your income details (e.g. <i>'25000 project payment'</i>):"
    )
    await state.set_state(IncomeState.details)

@router.message(Command("expense"))
async def cmd_expense(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        await process_expense(message, parts[1])
    else:
        await message.answer("Please provide expense details (e.g., <code>/expense 1500 Lunch</code>):")
        await state.set_state(ExpenseState.details)

@router.message(ExpenseState.details)
async def state_expense(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    await process_expense(message, message.text)
    await state.clear()

async def process_expense(message: Message, details: str):
    # 1. Deterministic Regex Amount Extraction
    amt_match = re.search(r'(?:Ksh|KES|\$)?\s*([\d,]+(?:\.\d+)?)', details, re.IGNORECASE)
    regex_amount = float(amt_match.group(1).replace(',', '')) if amt_match else None
    
    if not regex_amount or regex_amount <= 0.0:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
        return await message.answer(
            f"{SYMBOLS['alert']} Please specify a valid amount.\nExample: <code>/expense 1500 Lunch</code>",
            reply_markup=kb
        )

    status_msg = await message.answer(f"{SYMBOLS['ai']} Processing expense entry...")
    
    sys_prompt = (
        "Extract vendor and category from expense text. Return RAW JSON ONLY:\n"
        "{\"vendor\": \"string\", \"category\": \"food, transport, utilities, entertainment, shopping, health, education, or other\"}"
    )
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": details}
    ]
    
    try:
        response = await ai_client.generate_json(messages)
        if isinstance(response, dict):
            data = response
        else:
            cleaned = re.sub(r'```json|```', '', str(response)).strip()
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            data = json.loads(match.group(1)) if match else {}
            
        raw_amt = data.get("amount")
        ai_amt = abs(float(raw_amt)) if raw_amt is not None else None
        
        amount = regex_amount if regex_amount is not None else (ai_amt or 0.0)
        vendor = data.get("vendor") or details
        category = data.get("category") or "other"
        
        if amount <= 0.0:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
            return await status_msg.edit_text(f"{SYMBOLS['alert']} Invalid amount 0.00.", reply_markup=kb)

        query = """
        INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
        VALUES (?, ?, ?, ?, 'expense', ?, CURRENT_TIMESTAMP)
        """
        await db.execute(query, (message.from_user.id, amount, vendor, category, details))
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
        await status_msg.edit_text(
            f"<b>{SYMBOLS['success']} EXPENSE LOGGED SUCCESSFULLY</b>\n\n"
            f"<b>Amount   :</b> Ksh {amount:,.2f}\n"
            f"<b>Vendor   :</b> {safe_html(vendor)}\n"
            f"<b>Category :</b> {category.upper()}\n"
            f"<b>Status   :</b> Committed to Database",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Failed to parse manual expense: {e}")
        await status_msg.edit_text(f"{SYMBOLS['alert']} Could not parse details. Try format: <code>/expense 1500 Lunch</code>")

@router.message(Command("income"))
async def cmd_income(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        await process_income(message, parts[1])
    else:
        await message.answer("Please provide income details (e.g., <code>/income 25000 Project Payment</code>):")
        await state.set_state(IncomeState.details)

@router.message(IncomeState.details)
async def state_income(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    await process_income(message, message.text)
    await state.clear()

async def process_income(message: Message, details: str):
    # 1. Deterministic Regex Amount Extraction
    amt_match = re.search(r'(?:Ksh|KES|\$)?\s*([\d,]+(?:\.\d+)?)', details, re.IGNORECASE)
    regex_amount = float(amt_match.group(1).replace(',', '')) if amt_match else None
    
    if not regex_amount or regex_amount <= 0.0:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
        return await message.answer(
            f"{SYMBOLS['alert']} Please specify a valid amount.\nExample: <code>/income 25000 Project Payment</code>",
            reply_markup=kb
        )

    status_msg = await message.answer(f"{SYMBOLS['ai']} Processing income entry...")
    
    sys_prompt = (
        "Extract vendor/source and category from income text. Return RAW JSON ONLY:\n"
        "{\"vendor\": \"string\", \"category\": \"salary, freelance, investment, gift, or other\"}"
    )
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": details}
    ]
    
    try:
        response = await ai_client.generate_json(messages)
        if isinstance(response, dict):
            data = response
        else:
            cleaned = re.sub(r'```json|```', '', str(response)).strip()
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            data = json.loads(match.group(1)) if match else {}
            
        raw_amt = data.get("amount")
        ai_amt = abs(float(raw_amt)) if raw_amt is not None else None
        
        amount = regex_amount if regex_amount is not None else (ai_amt or 0.0)
        vendor = data.get("vendor") or details
        category = data.get("category") or "income"
        
        if amount <= 0.0:
            kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
            return await status_msg.edit_text(f"{SYMBOLS['alert']} Invalid amount 0.00.", reply_markup=kb)

        query = """
        INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
        VALUES (?, ?, ?, ?, 'income', ?, CURRENT_TIMESTAMP)
        """
        await db.execute(query, (message.from_user.id, amount, vendor, category, details))
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
        await status_msg.edit_text(
            f"<b>{SYMBOLS['success']} INCOME RECORDED</b>\n\n"
            f"<b>Amount   :</b> +Ksh {amount:,.2f}\n"
            f"<b>Source   :</b> {safe_html(vendor)}\n"
            f"<b>Category :</b> {category.upper()}\n"
            f"<b>Status   :</b> Committed to Database",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Income parse error: {e}")
        await status_msg.edit_text(f"{SYMBOLS['alert']} Could not parse income details.")

@router.callback_query(F.data == "fin:summary")
@router.message(Command("summary"))
async def cmd_summary(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    inc_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (user_id,), fetch=True)
    exp_res = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (user_id,), fetch=True)
    
    total_income = inc_res[0][0] if inc_res and inc_res[0][0] is not None else 0.0
    total_expense = exp_res[0][0] if exp_res and exp_res[0][0] is not None else 0.0
    net_flow = total_income - total_expense
    
    cat_query = """
    SELECT category, SUM(amount) as cat_total 
    FROM transactions 
    WHERE user_id = ? AND transaction_type = 'expense' 
    GROUP BY category 
    ORDER BY cat_total DESC
    """
    cat_results = await db.execute(cat_query, (user_id,), fetch=True)
    
    text = (
        f"<b>FINANCIAL SUMMARY REPORT</b>\n\n"
        f"<b>Total Income   :</b> +Ksh {total_income:,.2f}\n"
        f"<b>Total Expenses :</b> -Ksh {total_expense:,.2f}\n"
        f"<b>Net Cash Flow  :</b> Ksh {net_flow:,.2f}\n\n"
        f"<b>Expense Breakdown by Category:</b>\n"
    )
    
    if not cat_results:
        text += "• No expenses logged yet."
    else:
        for cat, amt in cat_results:
            pct = (amt / total_expense * 100) if total_expense > 0 else 0
            bar = make_progress_bar(pct, length=8)
            text += f"• <b>{cat.upper().ljust(12)}</b> Ksh {amt:,.2f}\n  └ {bar}\n\n"
            
    kb = build_sub_menu_kb([])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "fin:trends")
@router.message(Command("trends"))
async def cb_trends(event: Message | CallbackQuery):
    user_id = event.from_user.id
    daily_rows = await db.execute(
        "SELECT DATE(created_at) as tdate, transaction_type, SUM(amount) FROM transactions WHERE user_id = ? GROUP BY DATE(created_at), transaction_type ORDER BY tdate DESC LIMIT 10",
        (user_id,), fetch=True
    )
    
    text = "<b>Daily Spending Trends</b>\n\n"
    if not daily_rows:
        text += "No trend data recorded yet."
    else:
        daily_map = {}
        for r in daily_rows:
            d_str, ttype, amt = r[0], r[1], r[2] or 0.0
            if d_str not in daily_map:
                daily_map[d_str] = {"income": 0.0, "expense": 0.0}
            daily_map[d_str][ttype] = amt
            
        for date_key, val in daily_map.items():
            text += f"• <b>{date_key}:</b> -Ksh {val['expense']:,.2f} | +Ksh {val['income']:,.2f}\n"
            
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "fin:vendors")
async def cb_vendors(cb: CallbackQuery):
    user_id = cb.from_user.id
    vendor_rows = await db.execute(
        "SELECT vendor, SUM(amount), COUNT(*) FROM transactions WHERE user_id = ? AND transaction_type = 'expense' GROUP BY vendor ORDER BY SUM(amount) DESC LIMIT 5",
        (user_id,), fetch=True
    )
    
    text = "<b>Top Expense Vendors & Reasons</b>\n\n"
    if not vendor_rows:
        text += "No vendor data recorded yet."
    else:
        for idx, (v, amt, cnt) in enumerate(vendor_rows, 1):
            text += f"{idx}. <b>{safe_html(v or 'General')}</b>: Ksh {amt:,.2f} ({cnt} txns)\n"
            
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")]])
    await cb.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "fin:history")
@router.message(Command("history", "txns"))
async def cmd_history(event: Message | CallbackQuery):
    user_id = event.from_user.id
    query = "SELECT id, transaction_code, amount, vendor, category, transaction_type, transaction_date FROM transactions WHERE user_id = ? ORDER BY id DESC LIMIT 10"
    rows = await db.execute(query, (user_id,), fetch=True)
    
    if not rows:
        text = "<b>📜 TRANSACTION HISTORY</b>\n\nNo transaction history recorded yet."
        kb = build_sub_menu_kb([])
        if isinstance(event, Message):
            return await event.answer(text, reply_markup=kb)
        else:
            return await event.message.edit_text(text, reply_markup=kb)
            
    text = f"<b>📜 RECENT TRANSACTIONS HISTORY</b>\n\n"
    kb_rows = []
    
    for idx, r in enumerate(rows, 1):
        tid, code, amt, vendor, cat, ttype, created = r
        icon = "📥" if ttype == "income" else "📤"
        code_str = f" [<code>{code}</code>]" if code else ""
        text += f"{idx}. {icon} <b>{safe_html(vendor or 'Unknown')}</b>{code_str}\n"
        text += f"   └ Amount: <b>Ksh {amt:,.2f}</b> | Category: {cat.upper()}\n\n"
        kb_rows.append([InlineKeyboardButton(text=f"🗑️ Delete #{idx}", callback_data=f"fin_del:{tid}")])
        
    kb_rows.append([InlineKeyboardButton(text="« Back to Finance", callback_data="menu:finance")])
    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data.startswith("fin_del:"))
async def cb_delete_txn(cb: CallbackQuery):
    tid = int(cb.data.split(":")[1])
    await db.execute("DELETE FROM transactions WHERE id = ?", (tid,))
    await cb.answer("Transaction record deleted.")
    await cmd_history(cb)

@router.callback_query(F.data == "fin:reset_confirm")
@router.message(Command("reset_transactions", "clear_finance"))
async def cmd_reset_transactions(event: Message | CallbackQuery):
    text = (
        f"<b>RESET ALL TRANSACTIONS</b>\n\n"
        f"Are you sure you want to permanently clear all financial transaction records? This action cannot be undone."
    )
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="🔴 Yes, Reset All Records", callback_data="fin:do_reset")],
        [InlineKeyboardButton(text="« Cancel & Go Back", callback_data="menu:finance")]
    ])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "fin:do_reset")
async def cb_do_reset(cb: CallbackQuery):
    user_id = cb.from_user.id
    await db.execute("DELETE FROM transactions WHERE user_id = ?", (user_id,))
    await cb.answer("All transaction records have been reset to zero!")
    text = f"<b>{SYMBOLS['success']} TRANSACTION HISTORY RESET TO ZERO</b>\n\nAll financial transaction records have been cleared."
    kb = build_sub_menu_kb([])
    await cb.message.edit_text(text, reply_markup=kb)
