import logging
import os
from aiogram import Router, F
from aiogram.types import Message
from aiogram.filters import Command
from aiogram.types import FSInputFile

from app.services.media_tools import media_tools
from app.services.knowledge_base import kb_service
from app.utils.formatters import SYMBOLS

logger = logging.getLogger(__name__)
router = Router()

@router.message(Command("yt"))
async def cmd_yt_download(message: Message):
    """Download audio from YouTube."""
    parts = message.text.split(maxsplit=1)
    url = parts[1] if len(parts) > 1 else None
    
    if not url:
        return await message.answer("Usage: <code>/yt &lt;youtube_url&gt;</code>")

    status_msg = await message.answer(f"Initiating audio extraction pipeline...")
    
    file_path = await media_tools.download_youtube_audio(url)
    
    await status_msg.delete()
    
    if file_path and os.path.exists(file_path):
        audio_file = FSInputFile(file_path)
        await message.answer_audio(audio_file)
        os.remove(file_path)
    else:
        await message.answer(f"{SYMBOLS['alert']} Subsystem Error: Extraction failed. Verify URL.")

@router.message(F.document)
async def handle_document(message: Message):
    """Process incoming documents (specifically PDFs)."""
    document = message.document
    if not document.file_name.endswith('.pdf'):
        return await message.answer("Only PDF document parsing is currently supported.")

    status_msg = await message.answer(f"Fetching document stream...")
    
    file = await message.bot.get_file(document.file_id)
    os.makedirs("storage/temp", exist_ok=True)
    file_path = f"storage/temp/{document.file_id}.pdf"
    
    await message.bot.download_file(file.file_path, file_path)
    
    await status_msg.edit_text(f"Executing OCR/Text extraction...")
    text = await media_tools.extract_text_from_pdf(file_path)
    
    if text:
        user_id = message.from_user.id
        await kb_service.add_document(
            user_id=user_id,
            file_name=document.file_name,
            file_type="pdf",
            raw_text=text,
            metadata={"source": "telegram_document"}
        )
        await status_msg.edit_text(
            f"<b>DOCUMENT PROCESSED</b>\n"
            f""
            f"Status: {SYMBOLS['success']} Complete\n"
            f"Data extracted: {len(text)} bytes\n"
            f"Action: Committed to Knowledge Base"
        )
    else:
        await status_msg.edit_text(f"{SYMBOLS['alert']} Error: Document is encrypted or empty.")

    if os.path.exists(file_path):
        os.remove(file_path)
