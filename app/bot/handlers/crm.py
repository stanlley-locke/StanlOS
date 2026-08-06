import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.utils.formatters import SYMBOLS, build_sub_menu_kb

router = Router()
logger = logging.getLogger(__name__)

class ContactState(StatesGroup):
    details = State()

@router.callback_query(F.data == "menu:crm")
async def cb_crm_menu(cb: CallbackQuery):
    text = (
        f"<b>NETWORK INTELLIGENCE (CRM)</b>\n"
        f"\n"
        f"Use the following commands to manage your network:\n"
        f"{SYMBOLS['bullet']} /contact &lt;name, details&gt; - Add new contact\n"
        f"{SYMBOLS['bullet']} /network - View contacts"
    )
    kb = build_sub_menu_kb([])
    await cb.message.edit_text(text, reply_markup=kb)

@router.message(Command("contact"))
async def cmd_contact(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        await process_contact(message, parts[1])
    else:
        await message.answer(f"Please provide contact details (e.g., 'John Doe, CEO at TechCorp'):")
        await state.set_state(ContactState.details)

@router.message(ContactState.details)
async def state_contact(message: Message, state: FSMContext):
    await process_contact(message, message.text)
    await state.clear()

async def process_contact(message: Message, details: str):
    # Simple split by comma for now, in a real app this could use AI extraction
    parts = [p.strip() for p in details.split(',')]
    name = parts[0]
    company = parts[1] if len(parts) > 1 else ""
    context = ", ".join(parts[2:]) if len(parts) > 2 else ""
    
    query = """
    INSERT INTO contacts (user_id, name, company, context_summary)
    VALUES (?, ?, ?, ?)
    """
    try:
        await db.execute(query, (message.from_user.id, name, company, context))
        await message.answer(
            f"<b>CONTACT SAVED</b>\n"
            f""
            f"Name    : {name}\n"
            f"Company : {company}\n"
            f"Status  : {SYMBOLS['success']} Committed"
        )
    except Exception as e:
        logger.error(f"Failed to save contact: {e}")
        await message.answer(f"{SYMBOLS['alert']} System Error: Database write failed.")

@router.message(Command("network"))
async def cmd_network(message: Message):
    user_id = message.from_user.id
    
    query = "SELECT name, company, context_summary FROM contacts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10"
    results = await db.execute(query, (user_id,), fetch=True)
    
    if not results:
        return await message.answer(f"No contacts found in your network.")
        
    text = (
        f"<b>YOUR NETWORK</b>\n"
        f"\n"
    )
    
    for row in results:
        name, company, context = row
        text += f"{SYMBOLS['bullet']} <b>{name}</b>"
        if company:
            text += f" ({company})"
        text += "\n"
        
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")]])
    await message.answer(text, reply_markup=kb)
