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
@router.message(Command("gamification", "games"))
async def cb_gamification_menu(event: Message | CallbackQuery):
    user_id = event.from_user.id
    res = await db.execute("SELECT points FROM users WHERE tg_id = ?", (user_id,), fetch=True)
    points = res[0][0] if res and res[0][0] is not None else 0
    
    text = (
        f"<b>Gamification & Interactive Arcade</b>\n\n"
        f"<b>Your Balance:</b> <code>{points} PTS</code>\n\n"
        f"Earn points by completing daily check-ins, solving math speed games, and answering AI trivia quizzes!\n\n"
        f"• /checkin - Claim daily bonus (+10 PTS)\n"
        f"• /math_game - Speed Math Challenge (+50 PTS)\n"
        f"• /trivia &lt;topic&gt; - AI Trivia Challenge (+10 PTS)\n"
        f"• /leaderboard - View top scoring players"
    )
    buttons = [
        [("Claim Daily Bonus", "game:checkin"), ("Speed Math Game", "game:math_start")],
        [("AI Trivia Quiz", "game:trivia"), ("Top Leaderboard", "game:leaderboard")]
    ]
    kb = build_sub_menu_kb(buttons)
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data == "game:math_start")
@router.message(Command("math_game"))
async def cb_math_game(event: Message | CallbackQuery):
    import random
    n1 = random.randint(12, 45)
    n2 = random.randint(3, 15)
    n3 = random.randint(10, 50)
    ans = (n1 * n2) + n3
    
    # Wrong choices
    w1 = ans + random.choice([5, -5, 10])
    w2 = ans + random.choice([2, -3, 7])
    w3 = ans + random.choice([-10, 12, -4])
    
    choices = [ans, w1, w2, w3]
    random.shuffle(choices)
    
    text = (
        f"<b>Speed Math Challenge</b>\n\n"
        f"What is the result of:\n"
        f"<b>{n1} × {n2} + {n3} = ?</b>\n\n"
        f"Select the correct answer below (+50 PTS for correct answer!):"
    )
    btn_row = []
    for c in choices:
        is_correct = "1" if c == ans else "0"
        btn_row.append(InlineKeyboardButton(text=str(c), callback_data=f"math_ans:{is_correct}:{ans}"))
        
    kb = InlineKeyboardMarkup(inline_keyboard=[
        btn_row[:2],
        btn_row[2:],
        [InlineKeyboardButton(text="« Back to Games", callback_data="menu:gamification")]
    ])
    if isinstance(event, Message):
        await event.answer(text, reply_markup=kb)
    else:
        await event.message.edit_text(text, reply_markup=kb)

@router.callback_query(F.data.startswith("math_ans:"))
async def cb_math_answer(cb: CallbackQuery):
    _, is_correct, ans = cb.data.split(":")
    user_id = cb.from_user.id
    
    await db.execute("INSERT OR IGNORE INTO users (tg_id) VALUES (?)", (user_id,))
    
    if is_correct == "1":
        await increment_points(user_id, 50)
        await cb.answer("Correct! +50 PTS awarded!")
        text = f"<b>Correct Answer!</b>\n\n<b>Reward:</b> +50 PTS\n{ans} was indeed the correct calculation!"
    else:
        await cb.answer("Incorrect answer!")
        text = f"<b>Incorrect!</b>\n\nThe correct answer was: <code>{ans}</code>"
        
    kb = build_sub_menu_kb([[("Play Math Game Again", "game:math_start")]])
    await cb.message.edit_text(text, reply_markup=kb)

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
            f"<b>INCORRECT</b>\n\n"
            f"The correct answer was: <code>{safe_html(data.get('answer', 'N/A'))}</code>",
            reply_markup=kb
        )
    await state.clear()

@router.callback_query(F.data == "game:leaderboard")
@router.message(Command("leaderboard"))
async def cmd_leaderboard(event: Message | CallbackQuery):
    query = "SELECT full_name, username, points FROM users ORDER BY points DESC LIMIT 5"
    top_users = await db.execute(query, fetch=True)
    
    text = f"<b>STANLOS GAMIFICATION LEADERBOARD</b>\n\n"
    
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