from fastapi import APIRouter, Request, BackgroundTasks
import logging
from typing import Any

from app.services.finance import finance_service
from app.bot.dispatcher import bot
from app.core.config import settings
from app.utils.formatters import SYMBOLS, safe_html

logger = logging.getLogger(__name__)
router = APIRouter()

async def process_sms_background(sender: str, content: str):
    if not settings.ADMIN_IDS:
        logger.error("No ADMIN_IDS configured. Cannot assign SMS to a user.")
        return
        
    user_id = settings.ADMIN_IDS[0]
    
    result = await finance_service.parse_and_log_transaction(sender, content, user_id)
    if result:
        if result.get("is_duplicate"):
            dup_code = result.get("transaction_code", "N/A")
            msg = f"⚠️ <b>DUPLICATE TRANSACTION SKIPPED</b>\n\nTransaction code <code>{safe_html(dup_code)}</code> has already been logged in your database."
            try:
                await bot.send_message(chat_id=user_id, text=msg)
            except Exception as e:
                logger.error(f"Failed to send duplicate notification: {e}")
            return

        txn_type = result.get("type", "expense").upper()
        amount = result.get("amount", 0.0)
        fee = result.get("fee", 0.0)
        balance = result.get("balance")
        vendor = result.get("vendor", sender)
        category = result.get("category", "other").upper()
        txn_code = result.get("transaction_code", "N/A")
        
        icon = "📥" if txn_type == "INCOME" else "📤"
        
        msg = (
            f"<b>{icon} TRANSACTION LOGGED FROM SMS</b>\n\n"
            f"<b>Code     :</b> <code>{safe_html(txn_code or 'N/A')}</code>\n"
            f"<b>Type     :</b> {txn_type}\n"
            f"<b>Amount   :</b> Ksh {amount:,.2f}\n"
        )
        if fee and fee > 0:
            msg += f"<b>Fee      :</b> Ksh {fee:,.2f}\n"
        if balance is not None:
            msg += f"<b>Balance  :</b> Ksh {balance:,.2f}\n"
        msg += (
            f"<b>Vendor   :</b> {safe_html(vendor)}\n"
            f"<b>Category :</b> {category}\n"
            f"<b>Status   :</b> {SYMBOLS['success']} Committed to Database"
        )
        
        try:
            await bot.send_message(chat_id=user_id, text=msg)
        except Exception as e:
            logger.error(f"Failed to send Telegram notification: {e}")

def extract_sms_text(data: Any) -> tuple[str, str]:
    """Helper to extract sender and content from any JSON payload structure."""
    if not isinstance(data, dict):
        return "SMS", ""
        
    sender_keys = ["from", "sender", "address", "phone", "number", "originator"]
    content_keys = ["content", "message", "body", "text", "sms", "msg", "sms_body", "full_text"]
    
    sender = "SMS"
    for k in sender_keys:
        val = data.get(k)
        if val and isinstance(val, str) and not val.startswith(("{", "%", "$")):
            sender = val
            break
            
    content = ""
    for k in content_keys:
        val = data.get(k)
        if val and isinstance(val, str):
            content = val
            break
            
    # If content was inside a nested dictionary (e.g. data["payload"]["message"])
    if not content:
        for k, v in data.items():
            if isinstance(v, dict):
                s, c = extract_sms_text(v)
                if c:
                    return s, c
                    
    return sender, content

@router.post("/webhooks/sms")
async def sms_webhook(request: Request, background_tasks: BackgroundTasks):
    """
    Endpoint for SMS Forwarder Android App.
    """
    try:
        try:
            data = await request.json()
        except Exception:
            # Fallback for form-data or raw body
            body_bytes = await request.body()
            data = {"content": body_bytes.decode("utf-8", errors="ignore")}
            
        logger.info(f"Incoming SMS Webhook Payload: {data}")
        sender, content = extract_sms_text(data)
        
        # Check if content is a literal unreplaced placeholder string
        if not content or content.strip() in ["{body}", "%body%", "{content}", "%message%", "{message}", "$body"]:
            logger.warning(f"SMS webhook received empty or unreplaced placeholder content: '{content}'. Skipping processing.")
            return {"status": "ignored", "reason": "Content is empty or unreplaced template placeholder"}

        background_tasks.add_task(process_sms_background, sender, content)
        return {"status": "success", "message": "SMS received for processing"}
    except Exception as e:
        logger.error(f"Error handling SMS webhook: {e}")
        return {"status": "error", "message": str(e)}
