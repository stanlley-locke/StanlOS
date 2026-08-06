import logging
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, safe_html

router = Router()
logger = logging.getLogger(__name__)

class ContactState(StatesGroup):
    details = State()

@router.callback_query(F.data == "menu:crm")
@router.message(Command("crm"))
async def cb_crm_menu(event: Message | CallbackQuery):
    text = (
        f"<b>{SYMBOLS['notes']} NETWORK INTELLIGENCE (CRM)</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Manage your professional contacts, relationship context, and notes:\n\n"
        f"{SYMBOLS['bullet']} /contact &lt;details&gt; - Add contact (AI parsed)\n"
        f"{SYMBOLS['bullet']} /network - Browse saved contacts database"
    )
    buttons = [
        [("👤 Add New Contact", "crm:add_contact"), ("🌐 View Network", "crm:view_network")]
    ]
    kb = build_sub_menu_kb(buttons)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "crm:add_contact")
async def cb_add_contact(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        f"<b>👤 ADD CONTACT RECORD</b>\n\n"
        f"Please reply with contact details (e.g. <i>'John Doe, CTO at TechCorp, email: john@tech.com, met at TechSummit'</i>):"
    )
    await state.set_state(ContactState.details)

@router.message(Command("contact"))
async def cmd_contact(message: Message, state: FSMContext):
    parts = message.text.split(maxsplit=1)
    if len(parts) > 1:
        await process_contact(message, parts[1])
    else:
        await message.answer("Please provide contact details (e.g., <code>/contact Jane Smith, Lead Designer at Google</code>):")
        await state.set_state(ContactState.details)

@router.message(ContactState.details)
async def state_contact(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    await process_contact(message, message.text)
    await state.clear()

async def process_contact(message: Message, details: str):
    status_msg = await message.answer(f"{SYMBOLS['ai']} Extracting contact intelligence via AI...")
    
    sys_prompt = (
        "Extract contact details from the user's text. Return RAW JSON ONLY:\n"
        "{\n"
        "  \"name\": \"string (required)\",\n"
        "  \"company\": \"string\",\n"
        "  \"email\": \"string\",\n"
        "  \"phone\": \"string\",\n"
        "  \"context_summary\": \"string\"\n"
        "}"
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
            clean_json = str(response).replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
        
        name = data.get("name") or details.split(',')[0].strip()
        company = data.get("company", "")
        email = data.get("email", "")
        phone = data.get("phone", "")
        context = data.get("context_summary", details)
        
        query = """
        INSERT INTO contacts (user_id, name, company, email, phone, context_summary)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        await db.execute(query, (message.from_user.id, name, company, email, phone, context))
        
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to CRM", callback_data="menu:crm")]])
        await status_msg.edit_text(
            f"<b>{SYMBOLS['success']} CONTACT RECORD CREATED</b>\n\n"
            f"<b>Name    :</b> {safe_html(name)}\n"
            f"<b>Company :</b> {safe_html(company or 'N/A')}\n"
            f"<b>Email   :</b> {safe_html(email or 'N/A')}\n"
            f"<b>Phone   :</b> {safe_html(phone or 'N/A')}\n"
            f"<b>Context :</b> {safe_html(context[:150])}",
            reply_markup=kb
        )
    except Exception as e:
        logger.error(f"Failed to parse contact details: {e}")
        # Fallback simple insertion
        name = details.split(',')[0].strip()
        await db.execute("INSERT INTO contacts (user_id, name, context_summary) VALUES (?, ?, ?)", (message.from_user.id, name, details))
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to CRM", callback_data="menu:crm")]])
        await status_msg.edit_text(f"{SYMBOLS['success']} Contact '{safe_html(name)}' saved.", reply_markup=kb)

@router.callback_query(F.data == "crm:view_network")
@router.message(Command("network"))
async def cmd_network(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    query = "SELECT id, name, company, email, context_summary FROM contacts WHERE user_id = ? ORDER BY created_at DESC LIMIT 10"
    results = await db.execute(query, (user_id,), fetch=True)
    
    if not results:
        text = "<b>📇 NETWORK INTELLIGENCE</b>\n\nNo contacts recorded yet."
        buttons = [[("👤 Add New Contact", "crm:add_contact")]]
        kb = build_sub_menu_kb(buttons)
        if isinstance(event, Message):
            return await event.answer(text, reply_markup=kb)
        else:
            return await event.message.edit_text(text, reply_markup=kb)
        
    text = f"<b>📇 SAVED NETWORK CONTACTS</b>\n\n"
    
    kb_rows = []
    for idx, row in enumerate(results, 1):
        cid, name, company, email, context = row
        text += f"{idx}. <b>{safe_html(name)}</b>"
        if company:
            text += f" (<i>{safe_html(company)}</i>)"
        if email:
            text += f"\n   └ 📧 {safe_html(email)}"
        if context:
            text += f"\n   └ 📝 <i>\"{safe_html(context[:100])}\"</i>"
        text += "\n\n"
        kb_rows.append([InlineKeyboardButton(text=f"🗑️ Delete Contact #{idx}", callback_data=f"crm_del:{cid}")])
        
    kb_rows.append([InlineKeyboardButton(text="👤 Add Contact", callback_data="crm:add_contact")])
    kb_rows.append([InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")])
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    else:
        await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data.startswith("crm_del:"))
async def cb_delete_contact(cb: CallbackQuery):
    cid = int(cb.data.split(":")[1])
    await db.execute("DELETE FROM contacts WHERE id = ?", (cid,))
    await cb.answer("Contact removed from network.")
    await cmd_network(cb)
