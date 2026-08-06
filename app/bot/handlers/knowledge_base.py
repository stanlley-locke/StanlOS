import logging
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
import html

from app.services.knowledge_base import kb_service
from app.core.database import db
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, safe_html

logger = logging.getLogger(__name__)
router = Router()

class NoteState(StatesGroup):
    content = State()
    tags = State()

@router.callback_query(F.data == "menu:knowledge")
async def cb_knowledge_menu(cb: CallbackQuery):
    text = (
        f"<b>KNOWLEDGE BASE MANAGEMENT</b>\n"
        f"\n"
        f"Use the following commands to interact with memory:\n"
        f"{SYMBOLS['bullet']} /note &lt;text&gt; - Save a record\n"
        f"{SYMBOLS['bullet']} /find &lt;query&gt; - Semantic search"
    )
    kb = build_sub_menu_kb([])
    await cb.message.edit_text(text, reply_markup=kb)

@router.message(Command("note", "save"))
async def cmd_note(message: Message, state: FSMContext):
    """Start the note saving process."""
    parts = message.text.split(maxsplit=1)
    content = parts[1] if len(parts) > 1 else None
    
    if not content:
        return await message.answer(f"Usage: <code>/note &lt;your note here&gt;</code>")
        
    await state.update_data(content=content)
    await message.answer("Provide tags (comma separated) or send 'skip':")
    await state.set_state(NoteState.tags)

@router.message(NoteState.tags)
async def process_note_tags(message: Message, state: FSMContext):
    """Process tags and save note via KB service."""
    data = await state.get_data()
    content = data["content"]
    
    raw_tags = message.text.split(",") if message.text.lower() != "skip" else []
    tags = [t.strip() for t in raw_tags if t.strip()]
    
    user_id = message.from_user.id
    metadata = {"tags": tags, "source": "telegram"}
    
    success = await kb_service.add_document(
        user_id=user_id,
        file_name=f"Note_{message.message_id}",
        file_type="text",
        raw_text=content,
        metadata=metadata
    )
    
    if success:
        await message.answer(f"{SYMBOLS['success']} Record committed to Knowledge Base.")
    else:
        await message.answer(f"{SYMBOLS['alert']} Database write failed.")
        
    await state.clear()

@router.message(Command("find", "search"))
async def cmd_find(message: Message):
    """Search the Knowledge Base using semantic search."""
    parts = message.text.split(maxsplit=1)
    query = parts[1] if len(parts) > 1 else ""
    
    if not query:
        return await message.answer("Usage: <code>/find &lt;query&gt;</code>")

    status_msg = await message.answer(f"Executing semantic query against AI cluster...")
    
    user_id = message.from_user.id
    semantic_results = await kb_service.search_similar(user_id, query, top_k=3)
    
    await status_msg.delete()
    
    if not semantic_results:
        return await message.answer(f"No match for: <code>{safe_html(query)}</code>")
    
    text = (
        f"<b>SEARCH RESULTS: {safe_html(query).upper()}</b>\n"
        f"\n"
    )
    
    for res in semantic_results:
        clean_content = res['raw_text'].strip()[:150]
        score_pct = round(res['score'] * 100, 1)
        text += f"{SYMBOLS['bullet']} [Match: {score_pct}%] {safe_html(clean_content)}...\n\n"
            
    await message.answer(text)
