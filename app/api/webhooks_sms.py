from fastapi import APIRouter, Request, BackgroundTasks
import logging

from app.services.finance import finance_service
from app.bot.dispatcher import bot
from app.core.config import settings
from app.utils.formatters import SYMBOLS

logger = logging.getLogger(__name__)
router = APIRouter()

async def process_sms_background(sender: str, content: str):
    # We use the first admin ID as the default user for SMS transactions
    if not settings.ADMIN_IDS:
        logger.error("No ADMIN_IDS configured. Cannot assign SMS to a user.")
        return
        
    user_id = settings.ADMIN_IDS[0]
    
    result = await finance_service.parse_and_log_transaction(sender, content, user_id)
    if result:
        # Send confirmation to Telegram
        txn_type = result.get("type", "expense").capitalize()
        amount = result.get("amount", 0)
        vendor = result.get("vendor", "Unknown")
        
        msg = f"<b>TRANSACTION LOGGED (SMS)</b>\n"
        msg += f""
        msg += f"Type     : {txn_type}\n"
        msg += f"Amount   : {amount}\n"
        msg += f"Vendor   : {vendor}\n"
        msg += f"Category : {result.get('category', 'other')}\n"
        msg += f"Status   : {SYMBOLS['success']} Committed\n"
        
        try:
            await bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

@router.post("/webhooks/sms")
async def sms_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint for SmsForwarder App.
    Expected JSON payload: {"from": "SenderName", "content": "SMS Body"}
    """
    try:
        data = await request.json()
        sender = data.get("from", "Unknown")
        content = data.get("content", "")
        
        if content:
            # Process in background to avoid blocking the webhook response
            background_tasks.add_task(process_sms_background, sender, content)
            
        return {"status": "success", "message": "SMS received"}
    except Exception as e:
        logger.error(f"Error handling SMS webhook: {e}")
        return {"status": "error", "message": str(e)}
