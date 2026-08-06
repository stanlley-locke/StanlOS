import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import SYMBOLS, build_sub_menu_kb

router = Router()
logger = logging.getLogger(__name__)

class ExpenseState(StatesGroup):
    details = State()

@router.callback_query(F.data == "menu:finance")
async def cb_finance_menu(cb: CallbackQuery):
    text = (
        f"<b>FINANCE MODULE</b>\n"
        f"\n"
        f"Use the following commands to manage your finances:\n"
        f"{SYMBOLS['bullet']} /expense &lt;details&gt; - Log a manual expense\n"
        f"{SYMBOLS['bullet']} /summary - View financial summary\n\n"
        f"<i>Note: SMS transactions are logged automatically via webhooks.</i>"
    )
    kb = build_sub_menu_kb([])
    await cb.message.edit_text(text, reply_markup=kb)

@router.message(Command("expense"))
async def cmd_expense(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        await process_expense(message, parts[1])
    else:
        await message.answer(f"Please provide expense details (e.g., '1500 for lunch at KFC'):")
        await state.set_state(ExpenseState.details)

@router.message(ExpenseState.details)
async def state_expense(message: Message, state: FSMContext):
    await process_expense(message, message.text)
    await state.clear()

async def process_expense(message: Message, details: str):
    status_msg = await message.answer("Executing AI extraction of transaction data...")
    
    sys_prompt = (
        "You are a strict financial parser. Extract transaction details from the user's text.\n"
        "Output RAW JSON ONLY. No markdown formatting, no explanations. No emojis.\n"
        "Format:\n"
        "{\n"
        "  \"amount\": float,\n"
        "  \"vendor\": \"string\",\n"
        "  \"category\": \"food, transport, utilities, entertainment, shopping, health, education, or other\"\n"
        "}\n"
    )
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": details}
    ]
    
    try:
        response = await ai_client.generate_text(messages)
        import json
        clean_json = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        amount = float(data.get("amount", 0.0))
        vendor = data.get("vendor", "Unknown")
        category = data.get("category", "other")
        
        query = """
        INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
        VALUES (?, ?, ?, ?, 'expense', ?, CURRENT_TIMESTAMP)
        """
        await db.execute(query, (message.from_user.id, amount, vendor, category, details))
        
        await status_msg.edit_text(
            f"<b>TRANSACTION LOGGED</b>\n"
            f""
            f"Amount   : {amount}\n"
            f"Vendor   : {vendor}\n"
            f"Category : {category}\n"
            f"Status   : {SYMBOLS['success']} Committed"
        )
    except Exception as e:
        logger.error(f"Failed to parse manual expense: {e}")
        await status_msg.edit_text(f"{SYMBOLS['alert']} System Error: AI parser failed to understand the details.")

@router.message(Command("summary"))
async def cmd_summary(message: Message):
    user_id = message.from_user.id
    
    query = """
    SELECT category, SUM(amount) as total 
    FROM transactions 
    WHERE user_id = ? AND transaction_type = 'expense'
    GROUP BY category 
    ORDER BY total DESC
    """
    
    results = await db.execute(query, (user_id,), fetch=True)
    
    if not results:
        return await message.answer(f"No transaction records found.")
        
    text = (
        f"<b>EXPENSE SUMMARY</b>\n"
        f"\n"
    )
    
    grand_total = 0
    for row in results:
        cat, total = row
        grand_total += total
        text += f"{SYMBOLS['bullet']} {cat.upper().ljust(15)} : {total:.2f}\n"
        
    text += f"\n"
    text += f"TOTAL EXPENDITURE : {grand_total:.2f}"
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")]])
    await message.answer(text, reply_markup=kb)
