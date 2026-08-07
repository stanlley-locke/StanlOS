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
    """Creates a rich, professional financial executive dashboard text."""
    now = datetime.now().strftime("%a, %b %d, %Y | %H:%M")
    
    total_income = data.get("total_income", 0.0)
    total_expense = data.get("total_expense", 0.0)
    net_balance = total_income - total_expense
    
    pending_tasks_count = data.get("pending_tasks_count", 0)
    knowledge_count = data.get("knowledge_count", 0)
    contacts_count = data.get("contacts_count", 0)
    top_category = data.get("top_category", "None")
    top_cat_amount = data.get("top_cat_amount", 0.0)

    text = (
        f"<b>STANLOS EXECUTIVE CONSOLE</b>\n"
        f"<i>{now}</i>\n\n"
        f"<b>FINANCIAL INTELLIGENCE</b>\n"
        f"<code>  Net Balance  : Ksh {net_balance:,.2f}</code>\n"
        f"<code>  Cash Inflow  : +Ksh {total_income:,.2f}</code>\n"
        f"<code>  Cash Outflow : -Ksh {total_expense:,.2f}</code>\n"
        f"<code>  Top Expense  : {top_category.upper()} (Ksh {top_cat_amount:,.2f})</code>\n\n"
        f"<b>SYSTEM & WORKLOAD METRICS</b>\n"
        f"<code>  Active Tasks : {pending_tasks_count} pending</code>\n"
        f"<code>  RAG Memory   : {knowledge_count} documents</code>\n"
        f"<code>  CRM Network  : {contacts_count} contacts</code>"
    )
    return text

def build_main_menu_kb(is_admin: bool = True) -> InlineKeyboardMarkup:
    rows = [
        [
            InlineKeyboardButton(text="Workload", callback_data="menu:workload"),
            InlineKeyboardButton(text="Accounting", callback_data="menu:finance")
        ],
        [
            InlineKeyboardButton(text="Academic", callback_data="menu:academic"),
            InlineKeyboardButton(text="Knowledge RAG", callback_data="menu:knowledge")
        ],
        [
            InlineKeyboardButton(text="Contacts", callback_data="menu:crm"),
            InlineKeyboardButton(text="Media", callback_data="menu:media")
        ],
        [
            InlineKeyboardButton(text="App Store", callback_data="menu:apps"),
            InlineKeyboardButton(text="Forecasts", callback_data="menu:forecasts")
        ],
        [
            InlineKeyboardButton(text="Chat", callback_data="menu:ai_chat"),
            InlineKeyboardButton(text="Games", callback_data="menu:gamification")
        ]
    ]
    
    admin_row = []
    if is_admin:
        admin_row.append(InlineKeyboardButton(text="System Admin", callback_data="menu:devops"))
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
    rows.append([InlineKeyboardButton(text="« Back to Main Dashboard", callback_data="menu:main")])
    return InlineKeyboardMarkup(inline_keyboard=rows)
