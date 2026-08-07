import aiohttp
import logging
from typing import List, Dict, Optional, Any
from app.core.config import settings

logger = logging.getLogger(__name__)

class CloudflareAI:
    def __init__(self):
        self.account_id = settings.CLOUDFLARE_ACCOUNT_ID
        self.api_token = settings.CLOUDFLARE_API_TOKEN
        self.base_url = f"https://api.cloudflare.com/client/v4/accounts/{self.account_id}/ai/run"
        self.headers = {
            "Authorization": f"Bearer {self.api_token}",
            "Content-Type": "application/json"
        }

    async def _post(self, model: str, payload: dict) -> Optional[dict]:
        if not self.account_id or not self.api_token:
            logger.error("Cloudflare credentials missing.")
            return None

        url = f"{self.base_url}/{model}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, headers=self.headers, json=payload) as response:
                    response.raise_for_status()
                    data = await response.json()
                    if data.get("success"):
                        return data.get("result")
                    else:
                        logger.error(f"Cloudflare AI Error: {data.get('errors')}")
                        return None
        except Exception as e:
            logger.error(f"Error calling Cloudflare API: {e}")
            return None

    async def generate_text(self, messages: List[Dict[str, str]], model: str = None) -> Optional[str]:
        """
        Generate text using Llama 3 (or specified model).
        messages format: [{"role": "system", "content": "..."}, {"role": "user", "content": "..."}]
        """
        model = model or settings.CLOUDFLARE_MODEL_TEXT
        payload = {
            "messages": messages,
            "max_tokens": 2048
        }        
        result = await self._post(model, payload)
        if result and "response" in result:
            return result["response"]
        return None

    async def generate_json(self, messages: List[Dict[str, str]], model: str = None) -> Optional[dict]:
        """
        Forces JSON output by appending instructions and parsing the response.
        """
        # Append JSON instruction
        messages_copy = messages.copy()
        if messages_copy:
            messages_copy[0]["content"] += "\n\nYou MUST output valid JSON ONLY. No markdown wrappers. No explanations."
            
        raw_resp = await self.generate_text(messages_copy, model)
        if not raw_resp:
            return None
            
        if isinstance(raw_resp, dict):
            return raw_resp
            
        try:
            import json
            
            start = raw_resp.find('{')
            if start != -1:
                obj, _ = json.JSONDecoder().raw_decode(raw_resp[start:])
                return obj
            else:
                logger.info(f"AI response is plain text. Treating as Final Answer. Raw: {raw_resp}")
                return {"thought": "Generated response", "action": "Final Answer", "action_input": {"answer": raw_resp}}
                
        except Exception as e:
            logger.info(f"JSON parsing fallback triggered. Returning raw text as answer. Raw: {raw_resp}")
            
            import re
            match = re.search(r'"answer"\s*:\s*"([^"]*)', raw_resp)
            if match:
                answer_text = match.group(1).replace('\\n', '\n')
                return {"thought": "Generated response", "action": "Final Answer", "action_input": {"answer": answer_text}}
                
            return {"thought": "Generated response", "action": "Final Answer", "action_input": {"answer": raw_resp}}

    async def generate_embeddings(self, text: str, model: str = None) -> Optional[List[float]]:
        """
        Generate vector embeddings for RAG.
        """
        model = model or settings.CLOUDFLARE_MODEL_EMBEDDING
        payload = {"text": text}
        
        result = await self._post(model, payload)
        if result and "data" in result and len(result["data"]) > 0:
            return result["data"][0]
        return None

# Singleton instance
ai_client = CloudflareAI()
