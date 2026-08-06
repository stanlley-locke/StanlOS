import logging
import json
import re
from typing import Optional, Dict, Any

from app.services.ai_cloudflare import ai_client
from app.core.database import db

logger = logging.getLogger(__name__)

class FinanceService:
    async def parse_and_log_transaction(self, sender: str, sms_content: str, user_id: int) -> Optional[Dict[str, Any]]:
        """
        Uses Cloudflare AI to parse a transaction SMS and saves it to the database.
        """
        prompt = (
            "You are a strict financial data parser. Extract transaction details from the SMS below.\n"
            "Output RAW JSON ONLY. No markdown formatting, no explanations.\n"
            "Format:\n"
            "{\n"
            "  \"is_transaction\": true/false,\n"
            "  \"type\": \"income\" or \"expense\",\n"
            "  \"amount\": float,\n"
            "  \"vendor\": \"string (name of person or business)\",\n"
            "  \"category\": \"food, transport, utilities, entertainment, shopping, health, education, or other\",\n"
            "  \"date\": \"YYYY-MM-DD HH:MM:SS or null\"\n"
            "}\n"
            f"SMS Sender: {sender}\n"
            f"SMS Content: {sms_content}"
        )
        
        messages = [
            {"role": "system", "content": "You are a JSON-only financial parser."},
            {"role": "user", "content": prompt}
        ]
        
        raw_response = await ai_client.generate_text(messages)
        if not raw_response:
            logger.error("Failed to get response from AI for SMS parsing.")
            return None
            
        try:
            # Basic cleanup in case AI includes markdown blocks
            cleaned = re.sub(r'```json|```', '', raw_response).strip()
            # Find the JSON object
            match = re.search(r"(\{.*\})", cleaned, re.DOTALL)
            if not match:
                logger.error(f"No JSON found in response: {cleaned}")
                return None
                
            data = json.loads(match.group(1))
            
            if data.get("is_transaction"):
                amount = float(data.get("amount", 0.0))
                vendor = data.get("vendor", "Unknown")
                category = data.get("category", "other")
                txn_type = data.get("type", "expense")
                txn_date = data.get("date")
                
                # Save to database
                query = """
                INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
                VALUES (?, ?, ?, ?, ?, ?, ?)
                """
                await db.execute(query, (user_id, amount, vendor, category, txn_type, sms_content, txn_date))
                
                return data
            else:
                logger.info("SMS is not a transaction.")
                return None
                
        except Exception as e:
            logger.error(f"Error parsing transaction data: {e} | Raw: {raw_response}")
            return None

finance_service = FinanceService()
