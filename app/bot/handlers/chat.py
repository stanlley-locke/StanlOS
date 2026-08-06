from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
import logging
import asyncio

from app.agent.executor import agent
from app.utils.formatters import SYMBOLS

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
    
    status_msg = await message.answer(f"<b>[ @ ] AGENT STATUS</b>\n<i>Thought:</i> Initializing core systems...")
    
    async def status_callback(status: str):
        try:
            await status_msg.edit_text(status)
            await asyncio.sleep(0.5) # Prevent Telegram flood limits
        except Exception as e:
            pass
            
    final_response = await agent.run(user_text, status_callback=status_callback)
    
    await status_msg.delete()
    
    if final_response:
        await message.reply(
            f"<b>AGENT RESPONSE</b>\n"
            f"\n"
            f"{final_response}"
        )
    else:
        await message.reply(f"{SYMBOLS['alert']} System Error: AI backend offline or unresponsive.")
