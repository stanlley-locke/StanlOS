import logging
from datetime import datetime
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State
from dateutil import parser as dateparser

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import smart_edit, SYMBOLS, safe_html, build_sub_menu_kb

router = Router()
logger = logging.getLogger(__name__)

class AssignState(StatesGroup):
    title = State()
    deadline = State()

@router.callback_query(F.data == "menu:academic")
async def cb_academic_menu(cb: CallbackQuery):
    await cmd_assignments(cb)

@router.callback_query(F.data == "tasks:add")
@router.message(Command("assign"))
async def cmd_assign_start(event: Message | CallbackQuery, state: FSMContext):
    msg_target = event if isinstance(event, Message) else event.message
    await msg_target.answer(
        f"<b>➕ ADD NEW TASK / ASSIGNMENT</b>\n"
        
        f"Please enter the title or description of the task:"
    )
    await state.set_state(AssignState.title)

@router.message(AssignState.title)
async def assign_title(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    await state.update_data(title=message.text)
    await message.answer(
        f"<b>🕒 SET DUE DATE</b>\n\n"
        f"Enter deadline (e.g. <i>'Tomorrow 5pm'</i>, <i>'Friday 4pm'</i>, <i>'Nov 20'</i>):"
    )
    await state.set_state(AssignState.deadline)

def parse_relative_date(text: str) -> datetime:
    """Parses standard and relative dates (e.g. 'Tomorrow 5pm', 'Today at 9am')."""
    from datetime import timedelta
    text_lower = text.lower().strip()
    now = datetime.now()
    
    if "tomorrow" in text_lower:
        target_date = now + timedelta(days=1)
        if "5pm" in text_lower or "17" in text_lower:
            return target_date.replace(hour=17, minute=0, second=0)
        elif "9am" in text_lower:
            return target_date.replace(hour=9, minute=0, second=0)
        elif "pm" in text_lower:
            return target_date.replace(hour=18, minute=0, second=0)
        return target_date.replace(hour=17, minute=0, second=0)
    elif "today" in text_lower:
        if "9am" in text_lower:
            return now.replace(hour=9, minute=0, second=0)
        elif "5pm" in text_lower or "17" in text_lower:
            return now.replace(hour=17, minute=0, second=0)
        return now.replace(hour=23, minute=59, second=0)
        
    return dateparser.parse(text)

@router.message(AssignState.deadline)
async def assign_deadline(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return

    data = await state.get_data()
    try:
        deadline = parse_relative_date(message.text)
        formatted_date = deadline.strftime("%Y-%m-%d %H:%M")
        
        query = """
        INSERT INTO tasks (user_id, title, description, due_date, status, source_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        await db.execute(query, (message.from_user.id, data["title"], "", formatted_date, "pending", "academic"))
        
        kb = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📚 View All Tasks", callback_data="menu:academic")],
            [InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")]
        ])
        await message.answer(
            f"<b>{SYMBOLS['success']} TASK CREATED</b>\n\n"
            f"<b>Title:</b> {safe_html(data['title'])}\n"
            f"<b>Due Date:</b> {formatted_date}\n"
            f"<b>Status:</b> Pending",
            reply_markup=kb
        )
        await state.clear()
    except Exception as e:
        await message.answer(f"{SYMBOLS['alert']} Invalid date format. Example: <i>'Tomorrow at 4pm'</i> or <i>'Nov 15'</i>.")
        logger.warning(f"Date parse error: {e}")

@router.message(Command("assignments", "tasks"))
async def cmd_assignments(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    query = "SELECT id, title, due_date FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC"
    items = await db.execute(query, (user_id,), fetch=True)
    
    if not items:
        text = f"<b>📚 WORKLOAD & ASSIGNMENTS</b>\n\nNo pending tasks found. All clear!"
        buttons = [[("➕ Add New Task", "tasks:add")]]
        kb = build_sub_menu_kb(buttons)
        if isinstance(event, Message):
            return await event.answer(text, reply_markup=kb)
        else:
            return await event.message.edit_text(text, reply_markup=kb)
    
    kb_rows = []
    text = f"<b>📚 PENDING WORKLOAD & TASKS</b>\n\n"
    
    for idx, item in enumerate(items, 1):
        item_id, title, due_date = item
        text += f"{idx}. <b>{safe_html(title)}</b>\n   └ 🕒 Due: <code>{due_date}</code>\n\n"
        kb_rows.append([
            InlineKeyboardButton(text=f"Done #{idx}", callback_data=f"complete_task:{item_id}"),
            InlineKeyboardButton(text=f"🗑️ Delete #{idx}", callback_data=f"delete_task:{item_id}")
        ])
    
    kb_rows.append([InlineKeyboardButton(text=f"➕ Add New Task", callback_data="tasks:add")])
    kb_rows.append([InlineKeyboardButton(text=f"{SYMBOLS['ai']} Prioritize Workload with AI", callback_data="tasks:prioritize")])
    kb_rows.append([InlineKeyboardButton(text="« Back to Main Menu", callback_data="menu:main")])
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))
    else:
        await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb_rows))

@router.callback_query(F.data == "tasks:prioritize")
async def cb_prioritize(cb: CallbackQuery):
    user_id = cb.from_user.id
    
    query = "SELECT title, due_date FROM tasks WHERE user_id = ? AND status = 'pending'"
    items = await db.execute(query, (user_id,), fetch=True)
    
    if not items:
        return await cb.answer("No tasks available to prioritize.", show_alert=True)

    await cb.message.edit_text(f"{SYMBOLS['ai']} Analyzing workload urgency & creating schedule...")
    
    task_list = "\n".join([f"- {i[0]} (Due: {i[1]})" for i in items])
    sys_prompt = "You are an expert study and productivity coach. Prioritize these tasks based on urgency and importance. Provide clean bullet points."
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Prioritize these assignments:\n{task_list}"}
    ]
    
    recommendation = await ai_client.generate_text(messages)
    clean_rec = safe_html(recommendation or "No recommendation generated.")
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="« Back to Tasks", callback_data="menu:academic")]
    ])
    
    await cb.message.edit_text(
        f"<b>AI PRODUCTIVITY PLAN</b>\n\n{clean_rec}",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("complete_task:"))
async def cb_complete_task(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[1])
    
    query = "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (task_id,))
    
    await cb.answer("Task marked as completed! Points awarded.")
    await db.execute("UPDATE users SET points = points + 15 WHERE tg_id = ?", (cb.from_user.id,))
    await cmd_assignments(cb)

@router.callback_query(F.data.startswith("delete_task:"))
async def cb_delete_task(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[1])
    
    query = "DELETE FROM tasks WHERE id = ?"
    await db.execute(query, (task_id,))
    
    await cb.answer("Task removed.")
    await cmd_assignments(cb)