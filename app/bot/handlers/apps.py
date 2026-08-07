import logging
from aiogram import Router, F
from aiogram.types import CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from app.utils.formatters import build_sub_menu_kb, SYMBOLS

router = Router()
logger = logging.getLogger(__name__)

AVAILABLE_APPS = [
    {"id": "rss", "name": "📰 RSS News Feed", "desc": "Live news headlines for AI agent", "status": "Active"},
    {"id": "gmail", "name": "📧 Gmail Integration", "desc": "IMAP/SMTP Email Agent", "status": "Coming Soon"},
    {"id": "calendar", "name": "📅 Google Calendar", "desc": "Schedule & Meeting Management", "status": "Coming Soon"},
    {"id": "youtube", "name": "▶️ YouTube Services", "desc": "Video downloads and transcriptions", "status": "Active"}
]

@router.callback_query(F.data == "menu:apps")
async def cb_apps_menu(cb: CallbackQuery):
    text = (
        f"<b>🔌 APP STORE & INTEGRATIONS</b>\n"
        f"━━━━━━━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"Extend StanlOS capabilities by enabling apps. Once enabled, the AI Agent can autonomously use their tools.\n\n"
    )
    for app in AVAILABLE_APPS:
        status_icon = "✅" if app["status"] == "Active" else "🔒"
        text += f"{status_icon} <b>{app['name']}</b>\n  <i>{app['desc']}</i>\n\n"
        
    buttons = [
        [("Manage RSS", "apps:rss:config"), ("Manage Gmail", "apps:gmail:config")],
        [("YouTube Config", "apps:youtube:config")]
    ]
    kb = build_sub_menu_kb(buttons)
    await cb.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data.startswith("apps:"))
async def cb_app_config(cb: CallbackQuery):
    app_id = cb.data.split(":")[1]
    
    if app_id == "rss":
        text = "<b>📰 RSS News App</b>\n\nStatus: <b>ACTIVE</b>\n\nThe AI Agent is successfully connected to global RSS feeds. You can ask it for the latest news in Tech, Business, World, or AI."
    elif app_id == "youtube":
        text = "<b>▶️ YouTube Services</b>\n\nStatus: <b>ACTIVE</b>\n\nFallback oEmbed metadata routing and MP3 downloads are fully enabled."
    else:
        text = f"<b>{app_id.capitalize()} App</b>\n\nStatus: <b>IN DEVELOPMENT</b>\n\nThis app is scheduled for a future release."
        
    kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="« Back to App Store", callback_data="menu:apps")]])
    await cb.message.edit_text(text, reply_markup=kb)
