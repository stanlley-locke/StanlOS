import logging
import json
from aiogram import Router, F
from aiogram.types import Message, CallbackQuery, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import StatesGroup, State

from app.core.database import db
from app.services.ai_cloudflare import ai_client
from app.utils.formatters import SYMBOLS, build_sub_menu_kb, safe_html

router = Router()
logger = logging.getLogger(__name__)

class QuizState(StatesGroup):
    waiting_answer = State()

async def increment_points(user_id: int, points: int):
    query = "UPDATE users SET points = points + ? WHERE tg_id = ?"
    await db.execute(query, (points, user_id))

@router.callback_query(F.data == "menu:gamification")
@router.message(Command("gamification"))
async def cb_gamification_menu(event: Message | CallbackQuery):
    user_id = event.from_user.id
    res = await db.execute("SELECT points FROM users WHERE tg_id = ?", (user_id,), fetch=True)
    points = res[0][0] if res and res[0][0] is not None else 0
    
    text = (
        f"<b>{SYMBOLS['game']} GAMIFICATION & REWARDS</b>\n\n"
        f"<b>Your Current Balance:</b> <code>{points} PTS</code> 🏆\n\n"
        f"Earn points by completing daily check-ins, answering trivia quizzes, and finishing tasks!\n\n"
        f"{SYMBOLS['bullet']} /checkin - Claim daily 5 PTS bonus\n"
        f"{SYMBOLS['bullet']} /trivia &lt;topic&gt; - AI Trivia Challenge (+10 PTS)\n"
        f"{SYMBOLS['bullet']} /leaderboard - View top scoring users"
    )
    buttons = [
        [("✨ Claim Daily Bonus", "game:checkin"), ("❓ Play AI Trivia", "game:trivia")],
        [("🏆 Leaderboard", "game:leaderboard")]
    ]
    kb = build_sub_menu_kb(buttons)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "game:checkin")
@router.message(Command("checkin"))
async def cmd_checkin(event: Message | CallbackQuery):
    user_id = event.from_user.id
    await db.execute("INSERT OR IGNORE INTO users (tg_id, full_name, username) VALUES (?, ?, ?)", 
                     (user_id, event.from_user.full_name, event.from_user.username))
    await increment_points(user_id, 5)
    
    points_res = await db.execute("SELECT points FROM users WHERE tg_id = ?", (user_id,), fetch=True)
    total = points_res[0][0] if points_res else 5
    
    text = (
        f"<b>{SYMBOLS['success']} DAILY CHECK-IN COMPLETE!</b>\n\n"
        f"<b>Reward:</b> +5 PTS 🌟\n"
        f"<b>New Balance:</b> <code>{total} PTS</code>"
    )
    kb = build_sub_menu_kb([])
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text, reply_markup=kb)
    else:
        await event.answer(text, reply_markup=kb)

@router.callback_query(F.data == "game:trivia")
async def cb_trivia_start(cb: CallbackQuery, state: FSMContext):
    await cb.message.edit_text(
        f"<b>❓ AI TRIVIA CHALLENGE</b>\n\n"
        f"Reply with a topic for your trivia question (or send <i>'General Knowledge'</i>, <i>'Science'</i>, <i>'History'</i>, <i>'Coding'</i>):"
    )
    await state.set_state(QuizState.waiting_answer)

@router.message(Command("trivia"))
async def cmd_trivia(message: Message, state: FSMContext):
    """Start a Cloudflare-powered trivia quiz."""
    args = message.text.split(maxsplit=1)
    topic = args[1] if len(args) > 1 else "General Knowledge"
    await start_trivia(message, state, topic)

async def start_trivia(message: Message, state: FSMContext, topic: str):
    status_msg = await message.answer(f"{SYMBOLS['ai']} Generating trivia challenge for '{topic}'...")
    
    sys_prompt = (
        "Generate exactly one challenging trivia question and its short answer in RAW JSON:\n"
        "{\"question\": \"string\", \"answer\": \"string (max 5 words)\"}"
    )
    
    messages = [
        {"role": "system", "content": sys_prompt},
        {"role": "user", "content": f"Topic: {topic}"}
    ]
    
    try:
        response = await ai_client.generate_json(messages)
        if isinstance(response, dict):
            data = response
        else:
            clean_json = str(response).replace("```json", "").replace("```", "").strip()
            data = json.loads(clean_json)
        
        await status_msg.delete()
        await state.update_data(answer=data["answer"])
        await state.set_state(QuizState.waiting_answer)
        await message.answer(
            f"<b>❓ TRIVIA CHALLENGE: {safe_html(topic.upper())}</b>\n\n"
            f"<b>Question:</b> <i>{safe_html(data['question'])}</i>\n\n"
            f"Please reply with your answer (+10 PTS for correct answer!):"
        )
    except Exception as e:
        logger.error(f"Trivia error: {e}")
        await status_msg.edit_text(f"{SYMBOLS['alert']} Failed to generate trivia from AI backend.")
        await state.clear()

@router.message(QuizState.waiting_answer)
async def process_quiz(message: Message, state: FSMContext):
    if message.text and message.text.startswith('/'):
        await state.clear()
        return
    data = await state.get_data()
    user_ans = message.text.strip().lower()
    correct_ans = str(data.get("answer", "")).lower()
    
    await db.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (message.from_user.id,))
    
    kb = build_sub_menu_kb([])
    if correct_ans and (correct_ans in user_ans or user_ans in correct_ans):
        await increment_points(message.from_user.id, 10)
        await message.answer(
            f"<b>{SYMBOLS['success']} CORRECT ANSWER!</b>\n\n"
            f"<b>Reward:</b> +10 PTS 🎉\n"
            f"The correct answer was indeed: <code>{safe_html(data['answer'])}</code>",
            reply_markup=kb
        )
    else:
        await message.answer(
            f"<b>❌ INCORRECT</b>\n\n"
            f"The correct answer was: <code>{safe_html(data.get('answer', 'N/A'))}</code>",
            reply_markup=kb
        )
    await state.clear()

@router.callback_query(F.data == "game:leaderboard")
@router.message(Command("leaderboard"))
async def cmd_leaderboard(event: Message | CallbackQuery):
    query = "SELECT full_name, username, points FROM users ORDER BY points DESC LIMIT 5"
    top_users = await db.execute(query, fetch=True)
    
    text = f"<b>🏆 STANLOS GAMIFICATION LEADERBOARD</b>\n\n"
    
    if not top_users:
        text += "No high scores registered yet."
    else:
        medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]
        for idx, u in enumerate(top_users):
            fname, uname, pts = u
            name = fname or (f"@{uname}" if uname else "Anonymous")
            medal = medals[idx] if idx < len(medals) else "🏅"
            text += f"{medal} <b>{safe_html(name)}</b> — <code>{pts or 0} PTS</code>\n"
            
    kb = build_sub_menu_kb([])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)