from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import logging
import asyncio

from app.agent.executor import agent
from app.utils.formatters import SYMBOLS, safe_html

logger = logging.getLogger(__name__)
router = Router()

@router.callback_query(F.data == "menu:ai_chat")
async def cmd_ai_chat_menu(callback: CallbackQuery):
    await callback.message.edit_text(
        "<b>AI CHAT</b>\n\n"
        "Just type your message below to talk to StanlOS. The agent will process your request autonomously!"
    )
    await callback.answer()


@router.message(F.text)
async def handle_text_message(message: Message):
    """
    Handle generic text messages using the autonomous Agent Executor.
    """
    user_text = message.text
    
    status_msg = await message.answer(f"⚡ <b>STANLOS AGENT STATUS</b>\n\n<b>Thought :</b> <i>Initializing request context...</i>")
    
    async def status_callback(status: str):
        try:
            await status_msg.edit_text(status)
            await asyncio.sleep(0.5) # Prevent Telegram flood limits
        except Exception as e:
            pass
            
    final_response = await agent.run(user_text, user_id=message.from_user.id, status_callback=status_callback)
    
    try:
        await status_msg.delete()
    except Exception:
        pass
    
    if final_response:
        clean_response = safe_html(final_response)
        await message.reply(f"🤖 <b>AGENT RESPONSE</b>\n\n{clean_response}")
    else:
        await message.reply(f"{SYMBOLS['alert']} System Error: AI backend offline or unresponsive.")
