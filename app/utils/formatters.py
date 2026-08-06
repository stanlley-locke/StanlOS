import html
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Minimalist Professional UI Symbols
SYMBOLS = {
    "finance": "·",
    "academic": "·",
    "notes": "·",
    "devops": "·",
    "settings": "·",
    "help": "?",
    "ai": "·",
    "alert": "!",
    "success": "✓",
    "time": "·",
    "stats": "·",
    "knowledge": "·",
    "bullet": "•"
}

def safe_html(text: str) -> str:
    """Escapes HTML but preserves Telegram-supported tags."""
    if not text: return ""
    text = html.escape(str(text), quote=False)
    for tag in ['b', 'i', 'code', 'pre', 'u', 's', 'a']:
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return text

def format_dashboard(data: dict) -> str:
    """Creates a premium, minimalist 'Daily Briefing' dashboard text."""
    now = datetime.now().strftime("%B %d, %Y - %H:%M")
    
    finance_status = data.get("finance", "No recent activity")
    academic_status = data.get("academic", "All tasks complete")
    knowledge_count = data.get("knowledge_count", 0)

    text = (
        f"<b>STANLOS SYSTEM</b>\n"
        f"<i>{now}</i>\n\n"
        f"<b>Finance</b>\n"
        f"╰ {finance_status}\n\n"
        f"<b>Academic</b>\n"
        f"╰ {academic_status}\n\n"
        f"<b>Knowledge Base</b>\n"
        f"╰ {knowledge_count} records indexed\n\n"
        f"<i>Select a module to continue:</i>"
    )
    return text

def build_main_menu_kb(is_admin: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(text=f"{SYMBOLS['academic']} Tasks", callback_data="menu:academic"),
         InlineKeyboardButton(text=f"{SYMBOLS['finance']} Finance", callback_data="menu:finance")],
        [InlineKeyboardButton(text=f"{SYMBOLS['knowledge']} Knowledge", callback_data="menu:knowledge"),
         InlineKeyboardButton(text=f"{SYMBOLS['notes']} CRM", callback_data="menu:crm")],
        [InlineKeyboardButton(text=f"{SYMBOLS['ai']} AI Chat", callback_data="menu:ai_chat")]
    ]
    
    if is_admin:
        rows.append([InlineKeyboardButton(text=f"{SYMBOLS['devops']} System", callback_data="menu:devops")])
        
    rows.append([
        InlineKeyboardButton(text=f"{SYMBOLS['settings']} Settings", callback_data="menu:settings"),
        InlineKeyboardButton(text=f"{SYMBOLS['help']} Help", callback_data="menu:help")
    ])
    
    return InlineKeyboardMarkup(inline_keyboard=rows)

def build_sub_menu_kb(buttons: list) -> InlineKeyboardMarkup:
    """
    Helper to quickly build sub-menus with a back button.
    buttons: list of (text, callback_data) tuples.
    """
    rows = [[InlineKeyboardButton(text=text, callback_data=cb)] for text, cb in buttons]
    rows.append([InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
