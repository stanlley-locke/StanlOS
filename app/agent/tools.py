import logging
import json
from typing import Dict, Any, Callable, List

from app.services.web_service import web_service
from app.services.github_service import github_service
from app.services.userbot import userbot_service

logger = logging.getLogger(__name__)

class ToolRegistry:
    def __init__(self):
        self.tools: Dict[str, Callable] = {}
        self.tool_descriptions: List[Dict[str, Any]] = []

    def register(self, name: str, description: str):
        """Decorator to register a tool function."""
        def decorator(func):
            self.tools[name] = func
            self.tool_descriptions.append({
                "name": name,
                "description": description
            })
            return func
        return decorator

    async def execute(self, tool_name: str, **kwargs) -> str:
        """Executes a registered tool."""
        if tool_name not in self.tools:
            return f"Error: Tool '{tool_name}' not found."
        
        try:
            logger.info(f"Executing tool {tool_name} with args {kwargs}")
            # Ensure the function is awaited
            result = await self.tools[tool_name](**kwargs)
            return str(result)
        except Exception as e:
            logger.error(f"Error executing {tool_name}: {e}")
            return f"Error during execution: {str(e)}"

    def get_tool_prompt(self) -> str:
        """Formats tools for the ReAct prompt."""
        prompt = "You have access to the following tools:\n\n"
        for idx, tool in enumerate(self.tool_descriptions, 1):
            prompt += f"{idx}. {tool['name']}: {tool['description']}\n"
        return prompt

registry = ToolRegistry()

# Register core tools

@registry.register("search_web", "Searches the web using DuckDuckGo. Requires a 'query' string.")
async def search_web(query: str) -> str:
    results = await web_service.search_duckduckgo(query)
    if not results:
        return "No results found."
    
    formatted = []
    for r in results:
        formatted.append(f"Title/Snippet: {r['snippet']}\nURL: {r['url']}")
    return "\n---\n".join(formatted)

@registry.register("read_url", "Extracts readable text from a webpage URL. Requires a 'url' string.")
async def read_url(url: str) -> str:
    return await web_service.extract_text_from_url(url)

@registry.register("github_repo", "Fetches details of a GitHub repository. Requires 'owner' and 'repo' strings.")
async def github_repo(owner: str, repo: str) -> str:
    return await github_service.get_repo_info(owner, repo)

@registry.register("userbot_send", "Sends a Telegram message from your personal account. Requires 'chat_id' (string or int, like @username) and 'text' (string).")
async def userbot_send(chat_id: str | int, text: str) -> str:
    return await userbot_service.send_message(chat_id, text)

@registry.register("userbot_read", "Reads recent messages from a Telegram chat using your personal account. Requires 'chat_id' (string or int) and optional 'limit' (int).")
async def userbot_read(chat_id: str | int, limit: int = 5) -> str:
    return await userbot_service.get_history(chat_id, limit=limit)

@registry.register("get_system_stats", "Retrieves current server performance metrics including CPU usage, RAM, and Disk space. No arguments required.")
async def get_system_stats() -> str:
    import psutil
    import shutil
    from datetime import datetime
    
    cpu = psutil.cpu_percent(interval=1)
    ram = psutil.virtual_memory()
    disk = shutil.disk_usage("/")
    
    stats = (
        f"CPU Usage: {cpu}%\n"
        f"RAM Used: {ram.percent}% ({ram.used // (1024**2)}MB / {ram.total // (1024**2)}MB)\n"
        f"Disk Free: {disk.free // (1024**3)}GB / {disk.total // (1024**3)}GB\n"
        f"Uptime: {datetime.fromtimestamp(psutil.boot_time()).strftime('%Y-%m-%d %H:%M')}"
    )
    return stats
