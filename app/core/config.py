import os
import json
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

class Settings:
    # Telegram
    BOT_TOKEN: str = os.environ.get("BOT_TOKEN", "")
    
    @property
    def ADMIN_IDS(self) -> List[int]:
        val = os.environ.get("ADMIN_IDS", "[]")
        try:
            parsed = json.loads(val)
            if isinstance(parsed, list):
                return [int(x) for x in parsed]
            elif isinstance(parsed, int):
                return [parsed]
            else:
                return []
        except json.JSONDecodeError:
            return [int(x.strip()) for x in val.split(",") if x.strip().isdigit()]
            
    # MTProto Userbot
    API_ID: int = int(os.environ.get("API_ID", "0"))
    API_HASH: str = os.environ.get("API_HASH", "")
    PHONE_NUMBER: str = os.environ.get("PHONE_NUMBER", "")
            
    # Cloudflare AI
    CLOUDFLARE_ACCOUNT_ID: str = os.environ.get("CLOUDFLARE_ACCOUNT_ID", "")
    CLOUDFLARE_API_TOKEN: str = os.environ.get("CLOUDFLARE_API_TOKEN", "")
    CLOUDFLARE_MODEL_TEXT: str = os.environ.get("CLOUDFLARE_MODEL_TEXT", "@cf/meta/llama-3.1-8b-instruct")
    CLOUDFLARE_MODEL_EMBEDDING: str = os.environ.get("CLOUDFLARE_MODEL_EMBEDDING", "@cf/baai/bge-base-en-v1.5")
    
    # External Integrations
    GITHUB_TOKEN: str = os.environ.get("GITHUB_TOKEN", "")
    
    # Database
    SQLITE_CLOUD_CONN_STR: str = os.environ.get("SQLITE_CLOUD_CONN_STR", "")
    
    # App
    LOG_LEVEL: str = os.environ.get("LOG_LEVEL", "INFO")
    SECRET_KEY: str = os.environ.get("SECRET_KEY", "change_me_in_production")
    WEBHOOK_URL: str = os.environ.get("WEBHOOK_URL", "")

settings = Settings()
