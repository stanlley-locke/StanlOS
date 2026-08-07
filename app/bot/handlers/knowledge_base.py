import logging
import html
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.services.knowledge_base import kb_service
from app.core.database import db
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, safe_html, make_progress_bar

logger = logging.getLogger(__name__)
router = Router()

class NoteState(StatesGroup):
    content = State()
    tags = State()

@router.callback_query(F.data == "menu:knowledge")
@router.message(Command("knowledge"))
async def cb_knowledge_menu(event: Message | CallbackQuery):
    text = (
        f"<b>{SYMBOLS['knowledge']} MEMORY & KNOWLEDGE BASE (RAG)</b>\n"
        
        f"Store and retrieve knowledge using Cloudflare vector embeddings:\n\n"
        f"{SYMBOLS['bullet']} /note &lt;text&gt; - Save note into RAG memory\n"
        f"{SYMBOLS['bullet']} /find &lt;query&gt; - Perform semantic RAG search\n"
        f"{SYMBOLS['bullet']} /kblist - Browse all stored memory records\n\n"
        f"<i>Tip: Send any PDF document to automatically OCR and index it.</i>"
    )
    buttons = [
        [("📝 Save Note", "kb:add_note"), ("Semantic Search", "kb:search")],
        [("📚 Browse Index", "kb:list")]
    ]
    kb = build_sub_menu_kb(buttons)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "kb:add_note")
async def cb_add_note(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        f"<b>📝 SAVE NOTE TO MEMORY</b>\n\n"
        f"Please send the text content you wish to index into RAG memory:"
    )
    await state.set_state(NoteState.content)

@router.callback_query(F.data == "kb:search")
async def cb_search(cb: CallbackQuery):
    await cb.message.edit_text(
        f"<b>SEMANTIC RAG SEARCH</b>\n\n"
        f"Use the command format: <code>/find your query here</code>\n"
        f"Example: <code>/find project deadlines for November</code>"
    )

@router.message(Command("note", "save"))
async def cmd_note(message: Message, state: FSMContext):
    """Start the note saving process."""
    parts = message.text.split(maxsplit=1)
    content = parts[1] if len(parts) > 1 else None
    
    if not content:
        await message.answer("Please provide note text (e.g. <code>/note Meeting with Client on Friday at 3pm</code>):")
        await state.set_state(NoteState.content)
        return
        
    await state.update_data(content=content)
    await message.answer("Provide tags (comma separated) or send 'skip':")
    await state.set_state(NoteState.tags)

@router.message(NoteState.content)
async def process_note_content(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    await state.update_data(content=message.text)
    await message.answer("Provide tags (comma separated) or send 'skip':")
    await state.set_state(NoteState.tags)

@router.message(NoteState.tags)
async def process_note_tags(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    data = await state.get_data()
    content = data.get("content", "")
    
    raw_tags = message.text.split(",") if message.text.lower() != "skip" else []
    tags = [t.strip() for t in raw_tags if t.strip()]
    
    user_id = message.from_user.id
    metadata = {"tags": tags, "source": "telegram"}
    
    status_msg = await message.answer(f"{SYMBOLS['ai']} Generating vector embeddings via BGE Base En...")
    
    success = await kb_service.add_document(
        user_id=user_id,
        file_name=f"Note_{message.message_id}",
        file_type="text",
        raw_text=content,
        metadata=metadata
    )
    
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Knowledge Base", callback_data="menu:knowledge")]])
    if success:
        await status_msg.edit_text(
            f"<b>{SYMBOLS['success']} RECORD INDEXED IN RAG MEMORY</b>\n\n"
            f"<b>Content:</b> {safe_html(content[:150])}...\n"
            f"<b>Tags:</b> {', '.join(tags) if tags else 'None'}\n"
            f"<b>Vector Embeddings:</b> 768 Dimensions",
            reply_markup=kb
        )
    else:
        await status_msg.edit_text(f"{SYMBOLS['alert']} Database write failed.", reply_markup=kb)
        
    await state.clear()

@router.message(Command("find", "search"))
async def cmd_find(message: Message):
    """Search the Knowledge Base using semantic search."""
    parts = message.text.split(maxsplit=1)
    query = parts[1] if len(parts) > 1 else ""
    
    if not query:
        return await message.answer("Usage: <code>/find &lt;query&gt;</code> (e.g., <code>/find client meeting notes</code>)")

    status_msg = await message.answer(f"{SYMBOLS['ai']} Running vector similarity query...")
    
    user_id = message.from_user.id
    semantic_results = await kb_service.search_similar(user_id, query, top_k=3)
    
    await status_msg.delete()
    
    if not semantic_results:
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Knowledge Base", callback_data="menu:knowledge")]])
        return await message.answer(f"No semantic matches found for: <code>{safe_html(query)}</code>", reply_markup=kb)
    
    text = (
        f"<b>SEMANTIC SEARCH RESULTS</b>\n"
        f"<b>Query:</b> <i>{safe_html(query)}</i>\n\n"
    )
    
    for idx, res in enumerate(semantic_results, 1):
        clean_content = safe_html(res['raw_text'].strip()[:200])
        score_pct = round(res['score'] * 100, 1)
        bar = make_progress_bar(score_pct, length=8)
        text += f"<b>{idx}. Document:</b> <code>{res['file_name']}</code>\n"
        text += f"   └ <b>Relevance:</b> {bar}\n"
        text += f"   └ <i>\"{clean_content}...\"</i>\n\n"
            
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Knowledge Base", callback_data="menu:knowledge")]])
    await message.answer(text, reply_markup=kb)

@router.callback_query(F.data == "kb:list")
@router.message(Command("kblist", "documents"))
async def cmd_kb_list(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    query = "SELECT id, file_name, file_type, created_at FROM documents WHERE user_id = ? ORDER BY created_at DESC LIMIT 10"
    docs = await db.execute(query, (user_id,), fetch=True)
    
    if not docs:
        text = "<b>📚 MEMORY INDEX</b>\n\nNo records indexed yet."
        kb = build_sub_menu_kb([])
        if isinstance(event, Message):
            return await event.answer(text, reply_markup=kb)
        else:
            return await event.message.edit_text(text, reply_markup=kb)
            
    text = f"<b>📚 INDEXED MEMORY DOCUMENTS</b>\n\n"
    
    kb_rows = []
    for idx, doc in enumerate(docs, 1):
        doc_id, file_name, file_type, created_at = doc
        text += f"{idx}. <b>{safe_html(file_name)}</b> ({file_type.upper()})\n   └ Created: <code>{created_at}</code>\n\n"
        kb_rows.append([InlineKeyboardButton(text=f"🗑️ Delete Record #{idx}", callback_data=f"kb_del:{doc_id}")])
        
    kb_rows.append([InlineKeyboardButton(text="« Back to Knowledge Base", callback_data="menu:knowledge")])
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    else:
        await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data.startswith("kb_del:"))
async def cb_delete_kb(cb: CallbackQuery):
    doc_id = int(cb.data.split(":")[1])
    await db.execute("DELETE FROM documents WHERE id = ?", (doc_id,))
    await cb.answer("Document deleted from RAG index.")
    await cmd_kb_list(cb)
