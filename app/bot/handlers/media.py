import logging
import os
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.types import FSInputFile

from app.services.media_tools import media_tools
from app.services.knowledge_base import kb_service
from app.utils.formatters import smart_edit, SYMBOLS, build_sub_menu_kb, safe_html

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "menu:media")
@router.message(Command("media"))
async def cb_media_menu(event: Message | CallbackQuery):
    text = (
        f"<b>{SYMBOLS['media']} MEDIA & DOCUMENT PROCESSOR</b>\n\n"
        f"Extract audio or index documents into memory:\n\n"
        f"{SYMBOLS['bullet']} /yt &lt;url&gt; - Extract MP3 audio (YouTube, TikTok, Instagram, Twitter/X)\n"
        f"{SYMBOLS['bullet']} <b>Send PDF Document:</b> Upload any PDF in chat to OCR and index it into RAG memory."
    )
    buttons = [
        [("🎵 Social Media MP3 Extractor", "media:yt_help")]
    ]
    kb = build_sub_menu_kb(buttons)
    await smart_edit(event, text, reply_markup=kb)

@router.callback_query(F.data == "media:yt_help")
async def cb_yt_help(cb: CallbackQuery):
    await cb.message.edit_text(
        f"<b>🎵 MULTI-PLATFORM MEDIA AUDIO EXTRACTOR</b>\n\n"
        f"Extract audio from YouTube, TikTok, Instagram Reels, Twitter/X, and SoundCloud:\n\n"
        f"Usage: <code>/yt &lt;media_url&gt;</code>\n"
        f"Examples:\n"
        f"• <code>/yt https://www.youtube.com/watch?v=dQw4w9WgXcQ</code>\n"
        f"• <code>/yt https://www.tiktok.com/@user/video/7123456789</code>\n"
        f"• <code>/yt https://www.instagram.com/reel/C123456789</code>"
    )

@router.message(Command("yt", "download", "tiktok", "ig", "song", "music"))
async def cmd_yt_download(message: Message):
    """Download audio from YouTube, TikTok, Instagram, Twitter/X, SoundCloud or search songs."""
    parts = message.text.split(maxsplit=1)
    query = parts[1].strip() if len(parts) > 1 else None
    
    if not query:
        return await message.answer(
            "Usage:\n"
            "• Direct Link: <code>/yt https://www.youtube.com/watch?v=...</code>\n"
            "• Search Song: <code>/song Alan Walker Faded</code>"
        )

    if "..." in query or "example.com" in query or "<" in query:
        return await message.answer(f"{SYMBOLS['alert']} Please replace the example template with your real video URL or song title.")

    # Check if query is a direct URL or a search query
    if not (query.startswith("http://") or query.startswith("https://")):
        status_msg = await message.answer(f"{SYMBOLS['ai']} Searching SoundCloud for <i>'{safe_html(query)}'</i> (Bypassing YouTube bot blocks)...")
        results = await media_tools.search_soundcloud_songs(query, max_results=5)
        await status_msg.delete()
        
        if not results:
            return await message.answer(f"{SYMBOLS['alert']} No SoundCloud songs found matching <i>'{safe_html(query)}'</i>.")
            
        text_lines = [
            f"🎵 <b>SOUNDCLOUD MUSIC SEARCH</b>\n",
            f"Query: <i>{safe_html(query)}</i>\n"
        ]
        
        kb_rows = []
        for idx, track in enumerate(results, 1):
            text_lines.append(f"{idx}. <b>{safe_html(track['title'])}</b> ({track['duration']})\n   👤 <i>{safe_html(track['uploader'])}</i>\n")
            btn_title = (track['title'][:24] + "..") if len(track['title']) > 24 else track['title']
            
            # Use URL if it fits in 64 bytes, else fallback to API track URL
            callback_str = f"scdl:{track['url']}"
            if len(callback_str.encode('utf-8')) > 64:
                callback_str = f"scdl:https://api.soundcloud.com/tracks/{track['id']}"
                
            kb_rows.append([InlineKeyboardButton(text=f"🎵 {idx}. {btn_title} ({track['duration']})", callback_data=callback_str[:64])])
            
        text_lines.append("<i>Select a song below to download MP3 audio:</i>")
        kb_rows.append([InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")])
        kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
        return await message.answer("\n".join(text_lines), reply_markup=kb)

    status_msg = await message.answer(f"{SYMBOLS['ai']} Extracting audio stream via yt-dlp...")
    
    file_path, title, artist = await media_tools.download_media_audio(query)
    
    await status_msg.delete()
    
    if file_path and os.path.exists(file_path):
        safe_name = os.path.basename(file_path)
        audio_file = FSInputFile(file_path, filename=safe_name)
        caption_text = (
            f"🎵 <b>{safe_html(title)}</b>\n"
            f"👤 <i>{safe_html(artist)}</i>"
        )
        await message.answer_audio(
            audio_file,
            title=title,
            performer=artist,
            caption=caption_text
        )
        try:
            os.remove(file_path)
        except Exception:
            pass
    else:
        # FALLBACK: If YouTube blocks the download, extract the title and search SoundCloud automatically!
        if ("youtube.com" in query or "youtu.be" in query) and "Sign in to confirm" in str(title):
            fb_msg = await message.answer(f"{SYMBOLS['alert']} YouTube blocked the download due to datacenter IP checks.\n\n{SYMBOLS['ai']} Fetching video title via oEmbed to search SoundCloud instead...")
            yt_title = await media_tools.get_youtube_title_oembed(query)
            
            if yt_title:
                import re
                # Clean up title for better search results
                clean_title = re.sub(r'\(.*?\)|\[.*?\]', '', yt_title).replace("Official Video", "").replace("Official Music Video", "").strip()
                
                await fb_msg.edit_text(f"{SYMBOLS['ai']} Searching SoundCloud for: <i>'{safe_html(clean_title)}'</i>...")
                results = await media_tools.search_soundcloud_songs(clean_title, max_results=5)
                
                if results:
                    text_lines = [
                        f"🎵 <b>SOUNDCLOUD FALLBACK SEARCH</b>\n",
                        f"Original: <i>{safe_html(yt_title)}</i>\n"
                    ]
                    kb_rows = []
                    for idx, track in enumerate(results, 1):
                        text_lines.append(f"{idx}. <b>{safe_html(track['title'])}</b> ({track['duration']})\n   👤 <i>{safe_html(track['uploader'])}</i>\n")
                        btn_title = (track['title'][:24] + "..") if len(track['title']) > 24 else track['title']
                        
                        callback_str = f"scdl:{track['url']}"
                        if len(callback_str.encode('utf-8')) > 64:
                            callback_str = f"scdl:https://api.soundcloud.com/tracks/{track['id']}"
                            
                        kb_rows.append([InlineKeyboardButton(text=f"🎵 {idx}. {btn_title} ({track['duration']})", callback_data=callback_str[:64])])
                        
                    text_lines.append("<i>Select a song below to download MP3 audio:</i>")
                    kb_rows.append([InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")])
                    kb = InlineKeyboardMarkup(inline_keyboard=kb_rows)
                    await fb_msg.delete()
                    return await message.answer("\n".join(text_lines), reply_markup=kb)
                
            await fb_msg.edit_text(f"{SYMBOLS['alert']} Fallback failed. Could not find a SoundCloud alternative for this video.")
            return

        fail_text = f"{SYMBOLS['alert']} Extraction failed: {safe_html(title)}"
        await message.answer(fail_text)

@router.callback_query(F.data.startswith("scdl:"))
async def cb_scdl_download(cb: CallbackQuery):
    # Answer the callback IMMEDIATELY so Telegram doesn't throw a "query is too old" timeout error
    try:
        await cb.answer("Download started! This may take up to a minute...", show_alert=False)
    except Exception:
        pass

    url = cb.data.split(":", 1)[1]
    
    await cb.message.edit_text(f"{SYMBOLS['ai']} Downloading and converting audio stream to MP3 from SoundCloud...")
    
    file_path, title, artist = await media_tools.download_media_audio(url)
    
    if file_path and os.path.exists(file_path):
        safe_name = os.path.basename(file_path)
        audio_file = FSInputFile(file_path, filename=safe_name)
        caption_text = (
            f"🎵 <b>{safe_html(title)}</b>\n"
            f"👤 <i>{safe_html(artist)}</i>"
        )
        await cb.message.answer_audio(
            audio_file,
            title=title,
            performer=artist,
            caption=caption_text
        )
        try:
            await cb.message.delete()
        except Exception:
            pass
        try:
            os.remove(file_path)
        except Exception:
            pass
    else:
        await cb.message.edit_text(f"{SYMBOLS['alert']} Extraction failed. SoundCloud may be unavailable.")

@router.message(F.document)
async def handle_document(message: Message):
    """Process incoming documents (specifically PDFs)."""
    document = message.document
    if not document.file_name.lower().endswith('.pdf'):
        return await message.answer("Only PDF document parsing is currently supported.")

    status_msg = await message.answer(f"{SYMBOLS['ai']} Fetching PDF document stream...")
    
    file = await message.bot.get_file(document.file_id)
    os.makedirs("storage/temp", exist_ok=True)
    file_path = f"storage/temp/{document.file_id}.pdf"
    
    await message.bot.download_file(file.file_path, file_path)
    
    await status_msg.edit_text(f"{SYMBOLS['ai']} Performing OCR & text extraction...")
    text = await media_tools.extract_text_from_pdf(file_path)
    
    if text:
        user_id = message.from_user.id
        success = await kb_service.add_document(
            user_id=user_id,
            file_name=document.file_name,
            file_type="pdf",
            raw_text=text,
            metadata={"source": "telegram_document"}
        )
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]])
        await status_msg.edit_text(
            f"<b>{SYMBOLS['success']} PDF INDEXED IN MEMORY</b>\n\n"
            f"<b>File Name :</b> {safe_html(document.file_name)}\n"
            f"<b>Extracted :</b> {len(text):,} characters\n"
            f"<b>Status    :</b> Vectorized & Committed to Knowledge Base",
            reply_markup=kb
        )
    else:
        await status_msg.edit_text(f"{SYMBOLS['alert']} Failed to extract text from PDF (document may be empty or encrypted).")

    if os.path.exists(file_path):
        try:
            os.remove(file_path)
        except Exception:
            pass
