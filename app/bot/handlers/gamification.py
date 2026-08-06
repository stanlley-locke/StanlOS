import logging
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import SYMBOLS, build_sub_menu_kb

router = Router()
logger = logging.getLogger(__name__)

class QuizState(StatesGroup):
    waiting_answer = State()

async def increment_points(user_id: int, points: int):
    query = "UPDATE users SET points = points + ? WHERE tg_id = ?"
    await db.execute(query, (points, user_id))

@router.message(Command("trivia"))
async def cmd_trivia(message: Message, state: FSMContext):
    """Start a Cloudflare-powered trivia quiz."""
    args = message.text.split(maxsplit=1)
    topic = args[1] if len(args) > 1 else "General Knowledge"
    
    status_msg = await message.answer(f"{SYMBOLS['ai']} Generating challenge for '{topic}'...")
    
    sys_prompt = (
        "You are a quiz master. Generate exactly one challenging trivia question "
        "and its short answer. Return them in raw JSON format: "
        "{\"question\": \"...\", \"answer\": \"...\"}. "
        "Keep the answer very short (max 5 words). NO MARKDOWN BLOCKS. No emojis."
    )
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Topic: {topic}"}
    ]
    
    try:
        response = await ai_client.generate_text(messages)
        clean_json = response.replace("```json", "").replace("```", "").strip()
        data = json.loads(clean_json)
        
        await status_msg.delete()
        await state.update_data(answer=data["answer"])
        await state.set_state(QuizState.waiting_answer)
        await message.answer(
            f"<b>TRIVIA CHALLENGE: {topic.upper()}</b>\n"
            f"\n"
            f"Question: <i>{data['question']}</i>\n\n"
            f"Please reply with your answer."
        )
    except Exception as e:
        logger.error(f"Trivia error: {e}")
        await status_msg.edit_text("System Error: Failed to generate trivia from AI backend.")
        await state.clear()

@router.message(QuizState.waiting_answer)
async def process_quiz(message: Message, state: FSMContext):
    data = await state.get_data()
    user_ans = message.text.strip().lower()
    correct_ans = data["answer"].lower()
    
    # Ensure user exists first
    await db.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (message.from_user.id,))
    
    if correct_ans in user_ans or user_ans in correct_ans:
        await increment_points(message.from_user.id, 10)
        await message.answer(f"{SYMBOLS['success']} <b>CORRECT</b>\nYou have been awarded 10 points.")
    else:
        await message.answer(f"{SYMBOLS['alert']} <b>INCORRECT</b>\nThe correct answer was: <code>{data['answer']}</code>")
    await state.clear()

@router.message(Command("checkin"))
async def cmd_checkin(message: Message):
    await db.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (message.from_user.id,))
    await increment_points(message.from_user.id, 5)
    
    # Get current points
    points = await db.execute("SELECT points FROM users WHERE tg_id = ?", (message.from_user.id,), fetch=True)
    total = points[0][0] if points else 0
    
    await message.answer(
        f"{SYMBOLS['success']} Daily check-in complete. 5 points awarded.\n"
        f"Current Total Points: {total}"
    )