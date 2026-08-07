import html
from datetime import datetime
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

# Clean Minimalist UI Symbols
SYMBOLS = {
    "finance": "•",
    "academic": "•",
    "notes": "•",
    "devops": "•",
    "settings": "•",
    "help": "•",
    "ai": "•",
    "alert": "[!]",
    "success": "[OK]",
    "time": "•",
    "stats": "•",
    "knowledge": "•",
    "media": "•",
    "game": "•",
    "weather": "•",
    "calc": "•",
    "memory": "•",
    "bullet": "•",
    "arrow": "➔",
    "star": "★",
    "user": "•",
    "money_in": "(+)",
    "money_out": "(-)"
}

def safe_html(text: str) -> str:
    """Escapes HTML but preserves Telegram-supported tags safely."""
    if not text:
        return ""
    text = html.escape(str(text), quote=False)
    for tag in ['b', 'i', 'code', 'pre', 'u', 's', 'a']:
        text = text.replace(f"&lt;{tag}&gt;", f"<{tag}>").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
        text = text.replace(f"&lt;{tag} ", f"<{tag} ").replace(f"&lt;/{tag}&gt;", f"</{tag}>")
    return text

def make_progress_bar(percentage: float, length: int = 10) -> str:
    """Creates a visual ASCII progress bar."""
    filled = int(round(length * (percentage / 100)))
    bar = '█' * filled + '░' * (length - filled)
    return f"[{bar}] {percentage:.1f}%"

def format_key_value(data: dict, title: str = None, footer: str = None) -> str:
    """Formats a dictionary into clean key-value text."""
    lines = []
    if title:
        lines.append(f"<b>{title}</b>\n")
    for key, val in data.items():
        lines.append(f"<b>{key.ljust(12)}:</b> {safe_html(str(val))}")
    if footer:
        lines.append(f"\n<i>{footer}</i>")
    return "\n".join(lines)

def format_card(header: str, fields: dict, footer: str = None) -> str:
    """Formats structured data into a sleek layout."""
    lines = [f"<b>{header.upper()}</b>\n"]
    for key, val in fields.items():
        lines.append(f"<b>{key.ljust(12)}:</b> {safe_html(str(val))}")
    if footer:
        lines.append(f"\n<i>{footer}</i>")
    return "\n".join(lines)

def format_dashboard(data: dict) -> str:
    """Creates a sleek, minimalist dashboard briefing text."""
    now = datetime.now().strftime("%a, %b %d %Y | %H:%M")
    
    finance_status = data.get("finance", "No transactions logged")
    academic_status = data.get("academic", "All tasks up to date")
    knowledge_count = data.get("knowledge_count", 0)
    contacts_count = data.get("contacts_count", 0)
    pending_tasks_count = data.get("pending_tasks_count", 0)

    text = (
        f"<b>StanlOS</b>\n"
        f"<i>{now}</i>\n\n"
        f"• <b>Tasks:</b> {academic_status} ({pending_tasks_count} pending)\n"
        f"• <b>Finance:</b> {finance_status}\n"
        f"• <b>Memory:</b> {knowledge_count} documents indexed\n"
        f"• <b>Network:</b> {contacts_count} contacts recorded"
    )
    return text

def build_main_menu_kb(is_admin: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="Tasks & Academic", callback_data="menu:academic"),
            InlineKeyboardButton(text="Finance & MPESA", callback_data="menu:finance")
        ],
        [
            InlineKeyboardButton(text="Knowledge & RAG", callback_data="menu:knowledge"),
            InlineKeyboardButton(text="Network CRM", callback_data="menu:crm")
        ],
        [
            InlineKeyboardButton(text="Media Extractor", callback_data="menu:media"),
            InlineKeyboardButton(text="Tools & Utilities", callback_data="menu:tools")
        ],
        [
            InlineKeyboardButton(text="Gamification", callback_data="menu:gamification"),
            InlineKeyboardButton(text="AI Agent Terminal", callback_data="menu:ai_chat")
        ]
    ]
    
    admin_row = []
    if is_admin:
        admin_row.append(InlineKeyboardButton(text="DevOps", callback_data="menu:devops"))
    admin_row.append(InlineKeyboardButton(text="Settings", callback_data="menu:settings"))
    admin_row.append(InlineKeyboardButton(text="Help Guide", callback_data="menu:help"))
    rows.append(admin_row)
    
    return InlineKeyboardMarkup(inline_keyboard=rows)

def build_sub_menu_kb(buttons: list = None) -> InlineKeyboardMarkup:
    """Helper to build module sub-menus with a Back button."""
    rows = []
    if buttons:
        for btn in buttons:
            if isinstance(btn, list):
                rows.append([InlineKeyboardButton(text=text, callback_data=cb) for text, cb in btn])
            elif isinstance(btn, tuple):
                text, cb = btn
                rows.append([InlineKeyboardButton(text=text, callback_data=cb)])
    rows.append([InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
