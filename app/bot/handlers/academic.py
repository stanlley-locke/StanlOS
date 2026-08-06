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
from app.utils.formatters import SYMBOLS

router = Router()
logger = logging.getLogger(__name__)

class AssignState(StatesGroup):
    title = State()
    deadline = State()

@router.callback_query(F.data == "menu:academic")
async def cb_academic_menu(cb: CallbackQuery):
    await cmd_assignments(cb)

@router.message(Command("assign"))
async def cmd_assign_start(message: Message, state: FSMContext):
    await message.answer("Enter task/assignment title:")
    await state.set_state(AssignState.title)

@router.message(AssignState.title)
async def assign_title(message: Message, state: FSMContext):
    await state.update_data(title=message.text)
    await message.answer("Enter deadline (e.g., Friday 4pm, Nov 15):")
    await state.set_state(AssignState.deadline)

@router.message(AssignState.deadline)
async def assign_deadline(message: Message, state: FSMContext):
    if message.text.startswith('/'):
        await message.answer(f"{SYMBOLS['alert']} Please enter a valid date or time, not a command.")
        return

    data = await state.get_data()
    try:
        deadline = dateparser.parse(message.text)
        
        query = """
        INSERT INTO tasks (user_id, title, description, due_date, status, source_type)
        VALUES (?, ?, ?, ?, ?, ?)
        """
        await db.execute(query, (message.from_user.id, data["title"], "", deadline, "pending", "academic"))
        
        await message.answer(f"{SYMBOLS['success']} Assignment saved to your tasks.")
        await state.clear()
    except Exception as e:
        await message.answer(f"{SYMBOLS['alert']} Invalid date format. Please try again (e.g., Friday 4pm, Nov 15).")
        logger.warning(f"Date parse error: {e}")

@router.message(Command("assignments", "tasks"))
async def cmd_assignments(event: Message | CallbackQuery):
    user_id = event.from_user.id
    
    query = "SELECT id, title, due_date FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC"
    items = await db.execute(query, (user_id,), fetch=True)
    
    if not items:
        text = "<b>PENDING ASSIGNMENTS</b>\nNo pending tasks found."
        kb = InlineKeyboardMarkup(inline_keyboard=[[InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")]])
        if isinstance(event, Message):
            return await event.answer(text, reply_markup=kb)
        else:
            return await event.message.edit_text(text, reply_markup=kb)
    
    kb = []
    text = "<b>PENDING ASSIGNMENTS</b>\n\n"
    for item in items:
        item_id, title, due_date = item
        text += f"{SYMBOLS['bullet']} <b>{title}</b>\n  └ Due: {due_date}\n\n"
        kb.append([InlineKeyboardButton(text=f"[Complete] {title[:15]}...", callback_data=f"complete_task:{item_id}")])
    
    kb.append([InlineKeyboardButton(text=f"{SYMBOLS['ai']} Prioritize with AI", callback_data="tasks:prioritize")])
    kb.append([InlineKeyboardButton(text="< Back to Main", callback_data="menu:main")])
    
    if isinstance(event, Message):
        await event.answer(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))
    else:
        await event.message.edit_text(text, reply_markup=InlineKeyboardMarkup(inline_keyboard=kb))


@router.callback_query(F.data == "tasks:prioritize")
async def cb_prioritize(cb: CallbackQuery):
    user_id = cb.from_user.id
    
    query = "SELECT title, due_date FROM tasks WHERE user_id = ? AND status = 'pending'"
    items = await db.execute(query, (user_id,), fetch=True)
    
    if not items:
        return await cb.answer("No tasks available to prioritize.", show_alert=True)

    await cb.message.edit_text(f"{SYMBOLS['ai']} Analyzing workload...")
    
    task_list = "\n".join([f"- {i[0]} (Due: {i[1]})" for i in items])
    sys_prompt = "You are a professional study coach. Prioritize these tasks based on urgency. Keep it concise, using clear bullet points. Do not use emojis."
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Prioritize these assignments:\n{task_list}"}
    ]
    
    recommendation = await ai_client.generate_text(messages)
    
    kb = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="< Back to Tasks", callback_data="menu:academic")]
    ])
    
    await cb.message.edit_text(
        f"<b>AI STUDY PLAN</b>\n"
        f"\n"
        f"{recommendation}",
        reply_markup=kb
    )

@router.callback_query(F.data.startswith("complete_task:"))
async def cb_complete_task(cb: CallbackQuery):
    task_id = int(cb.data.split(":")[1])
    
    query = "UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE id = ?"
    await db.execute(query, (task_id,))
    
    await cb.answer("Task marked as complete.")
    await cmd_assignments(cb)