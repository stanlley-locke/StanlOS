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


# Short-term conversational memory
chat_memory = {}

@router.message(F.text)
async def handle_text_message(message: Message):
    """
    Handle generic text messages using the autonomous Agent Executor.
    """
    user_text = message.text.strip()
    user_id = message.from_user.id
    
    # Ignore slash commands so they don't trigger AI agent loop
    if user_text.startswith('/'):
        return
        
    if user_id not in chat_memory:
        chat_memory[user_id] = []
    
    status_msg = await message.answer("<b>StanlOS Agent</b>\n\n<i>Processing request...</i>")
    
    async def status_callback(status: str):
        try:
            await status_msg.edit_text(f"<b>StanlOS Agent</b>\n\n<i>{status}</i>")
            await asyncio.sleep(0.4)
        except Exception:
            pass
            
    # Get current history
    history = chat_memory[user_id]
            
    final_response = await agent.run(user_text, user_id=user_id, status_callback=status_callback, chat_history=history)
    
    # Append to memory (limit to 5 pairs = 10 messages)
    chat_memory[user_id].append({"role": "user", "content": user_text})
    if final_response:
        chat_memory[user_id].append({"role": "assistant", "content": final_response})
        
    if len(chat_memory[user_id]) > 10:
        chat_memory[user_id] = chat_memory[user_id][-10:]
        
    
    try:
        await status_msg.delete()
    except Exception:
        pass
    
    if final_response:
        clean_response = safe_html(final_response)
        await message.reply(f"<b>Agent Response:</b>\n\n{clean_response}")
    else:
        await message.reply("System Error: AI backend offline or unresponsive.")
