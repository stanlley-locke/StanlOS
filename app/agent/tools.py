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
            func = self.tools[tool_name]
            import inspect
            sig = inspect.signature(func)
            has_kwargs = any(p.kind == inspect.Parameter.VAR_KEYWORD for p in sig.parameters.values())
            if not has_kwargs:
                filtered_kwargs = {k: v for k, v in kwargs.items() if k in sig.parameters}
            else:
                filtered_kwargs = kwargs
            result = await func(**filtered_kwargs)
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

@registry.register("userbot_send", "DO NOT use to reply to current user. Sends an external Telegram message to ANOTHER third-party recipient/channel. Requires 'chat_id' (string or int, like @username) and 'text' (string).")
async def userbot_send(chat_id: str | int, text: str) -> str:
    return await userbot_service.send_message(chat_id, text)

@registry.register("userbot_read", "Reads recent messages from a Telegram chat using your personal account. Requires 'chat_id' (string or int) and optional 'limit' (int).")
async def userbot_read(chat_id: str | int, limit: int | str = 5) -> str:
    try:
        limit_int = int(limit)
    except Exception:
        limit_int = 5
    return await userbot_service.get_history(chat_id, limit=limit_int)

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

@registry.register("remember_fact", "Saves a personal fact or preference into long-term memory. Requires 'user_id' (int), 'fact_key' (string), and 'fact_value' (string).")
async def remember_fact(user_id: int | str, fact_key: str, fact_value: str) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        query = "INSERT INTO memories (user_id, fact_key, fact_value) VALUES (?, ?, ?)"
        await db.execute(query, (uid, fact_key.strip().lower(), fact_value.strip()))
        return f"Memory saved: {fact_key} = {fact_value}"
    except Exception as e:
        return f"Failed to save memory: {e}"

@registry.register("recall_fact", "Retrieves stored facts/memories. Requires 'user_id' (int) and optional 'fact_key' (string).")
async def recall_fact(user_id: int | str, fact_key: str = "") -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        if fact_key:
            query = "SELECT fact_key, fact_value FROM memories WHERE user_id = ? AND fact_key LIKE ? ORDER BY created_at DESC LIMIT 5"
            rows = await db.execute(query, (uid, f"%{fact_key.strip().lower()}%"), fetch=True)
        else:
            query = "SELECT fact_key, fact_value FROM memories WHERE user_id = ? ORDER BY created_at DESC LIMIT 5"
            rows = await db.execute(query, (uid,), fetch=True)
        
        if not rows:
            return "No memories found."
        return "\n".join([f"• {k}: {v}" for k, v in rows])
    except Exception as e:
        return f"Failed to recall memory: {e}"

@registry.register("get_weather", "Fetches current weather forecast for any location. Requires 'location' string (e.g. 'Nairobi', 'London').")
async def get_weather(location: str) -> str:
    import aiohttp
    try:
        async with aiohttp.ClientSession() as session:
            # Geocoding API
            geo_url = f"https://geocoding-api.open-meteo.com/v1/search?name={location}&count=1"
            async with session.get(geo_url) as resp:
                geo_data = await resp.json()
                if not geo_data.get("results"):
                    return f"Location '{location}' not found."
                loc = geo_data["results"][0]
                lat, lon = loc["latitude"], loc["longitude"]
                name = loc.get("name", location)
                country = loc.get("country", "")

            # Weather API
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            async with session.get(weather_url) as resp:
                w_data = await resp.json()
                cw = w_data.get("current_weather", {})
                temp = cw.get("temperature", "N/A")
                wind = cw.get("windspeed", "N/A")
                return f"Weather in {name}, {country}: {temp}°C, Wind Speed: {wind} km/h."
    except Exception as e:
        return f"Weather lookup failed: {e}"

@registry.register("calculate", "Evaluates a mathematical expression safely. Requires 'expression' string (e.g. '1500 * 0.16 + 50').")
async def calculate(expression: str) -> str:
    import ast
    import operator as op
    
    operators = {
        ast.Add: op.add, ast.Sub: op.sub, ast.Mult: op.mul,
        ast.Div: op.truediv, ast.Pow: op.pow, ast.USub: op.neg
    }
    
    def _eval(node):
        if isinstance(node, ast.Num):
            return node.n
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.BinOp):
            return operators[type(node.op)](_eval(node.left), _eval(node.right))
        elif isinstance(node, ast.UnaryOp):
            return operators[type(node.op)](_eval(node.operand))
        else:
            raise TypeError(node)

    try:
        expr_clean = expression.replace("^", "**")
        parsed = ast.parse(expr_clean, mode='eval')
        res = _eval(parsed.body)
        return f"Result: {res}"
    except Exception as e:
        return f"Calculation error: {e}"

# Domain Action Tools

@registry.register("log_expense", "Logs a financial expense entry. Requires 'user_id' (int), 'amount' (float), 'vendor' (string), and optional 'category' (string).")
async def log_expense(user_id: int | str, amount: float | str, vendor: str, category: str = "other") -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        amt = abs(float(amount))
        query = """
        INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
        VALUES (?, ?, ?, ?, 'expense', ?, CURRENT_TIMESTAMP)
        """
        await db.execute(query, (uid, amt, vendor.strip(), category.strip().lower(), f"Manual AI log: {vendor}"))
        return f"Logged expense of Ksh {amt:,.2f} for '{vendor}' under {category.upper()}."
    except Exception as e:
        return f"Failed to log expense: {e}"

@registry.register("log_income", "Logs a financial income entry. Requires 'user_id' (int), 'amount' (float), 'vendor' (string), and optional 'category' (string).")
async def log_income(user_id: int | str, amount: float | str, vendor: str, category: str = "income") -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        amt = abs(float(amount))
        query = """
        INSERT INTO transactions (user_id, amount, vendor, category, transaction_type, raw_sms, transaction_date)
        VALUES (?, ?, ?, ?, 'income', ?, CURRENT_TIMESTAMP)
        """
        await db.execute(query, (uid, amt, vendor.strip(), category.strip().lower(), f"Manual AI log: {vendor}"))
        return f"Recorded income of +Ksh {amt:,.2f} from '{vendor}' under {category.upper()}."
    except Exception as e:
        return f"Failed to log income: {e}"

@registry.register("get_financial_summary", "Fetches summary of income, expenses, and cash flow for a user. Requires 'user_id' (int).")
async def get_financial_summary(user_id: int | str) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        inc = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'income'", (uid,), fetch=True)
        exp = await db.execute("SELECT SUM(amount) FROM transactions WHERE user_id = ? AND transaction_type = 'expense'", (uid,), fetch=True)
        
        total_inc = inc[0][0] if inc and inc[0][0] is not None else 0.0
        total_exp = exp[0][0] if exp and exp[0][0] is not None else 0.0
        net = total_inc - total_exp
        
        return f"Income: +Ksh {total_inc:,.2f} | Expenses: -Ksh {total_exp:,.2f} | Net Cash Flow: Ksh {net:,.2f}"
    except Exception as e:
        return f"Failed to get summary: {e}"

@registry.register("add_task", "Adds a new task/assignment. Requires 'user_id' (int), 'title' (string), and 'due_date' (string, e.g. 'Tomorrow 5pm').")
async def add_task(user_id: int | str, title: str, due_date: str) -> str:
    from app.core.database import db
    from app.bot.handlers.academic import parse_relative_date
    try:
        uid = int(user_id)
        d_time = parse_relative_date(due_date)
        formatted_date = d_time.strftime("%Y-%m-%d %H:%M")
        query = "INSERT INTO tasks (user_id, title, due_date, status, source_type) VALUES (?, ?, ?, 'pending', 'academic')"
        await db.execute(query, (uid, title.strip(), formatted_date))
        return f"Created task '{title}' due on {formatted_date}."
    except Exception as e:
        return f"Failed to add task: {e}"

@registry.register("list_tasks", "Lists pending tasks. Requires 'user_id' (int).")
async def list_tasks(user_id: int | str) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        rows = await db.execute("SELECT id, title, due_date FROM tasks WHERE user_id = ? AND status = 'pending' ORDER BY due_date ASC", (uid,), fetch=True)
        if not rows:
            return "No pending tasks."
        return "\n".join([f"• #{r[0]}: {r[1]} (Due: {r[2]})" for r in rows])
    except Exception as e:
        return f"Failed to list tasks: {e}"

@registry.register("delete_task", "Deletes a task by ID or deletes all tasks. Requires 'user_id' (int), optional 'task_id' (int/string), or 'all_tasks' (bool).")
async def delete_task(user_id: int | str, task_id: int | str = None, all_tasks: bool = False) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        if all_tasks or (task_id and str(task_id).lower() in ["all", "everything", "*", "true"]):
            await db.execute("DELETE FROM tasks WHERE user_id = ?", (uid,))
            return "All tasks have been deleted from your task list."
        elif task_id and str(task_id).isdigit():
            tid = int(task_id)
            await db.execute("DELETE FROM tasks WHERE user_id = ? AND id = ?", (uid, tid))
            return f"Task #{tid} has been deleted."
        else:
            # Delete latest task if no ID specified
            await db.execute("DELETE FROM tasks WHERE user_id = ? ORDER BY id DESC LIMIT 1", (uid,))
            return "Latest task has been deleted."
    except Exception as e:
        return f"Failed to delete task: {e}"

@registry.register("complete_task", "Marks a task as completed. Requires 'user_id' (int) and 'task_id' (int).")
async def complete_task(user_id: int | str, task_id: int | str) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        tid = int(task_id)
        await db.execute("UPDATE tasks SET status = 'completed', completed_at = CURRENT_TIMESTAMP WHERE user_id = ? AND id = ?", (uid, tid))
        return f"Task #{tid} marked as completed."
    except Exception as e:
        return f"Failed to complete task: {e}"

@registry.register("clear_tasks", "Clears all pending and completed tasks for a user. Requires 'user_id' (int).")
async def clear_tasks(user_id: int | str) -> str:
    from app.core.database import db
    try:
        uid = int(user_id)
        await db.execute("DELETE FROM tasks WHERE user_id = ?", (uid,))
        return "All tasks have been cleared."
    except Exception as e:
        return f"Failed to clear tasks: {e}"

@registry.register("search_memory", "Performs semantic search over RAG indexed documents. Requires 'user_id' (int) and 'query' (string).")
async def search_memory(user_id: int | str, query: str) -> str:
    from app.services.knowledge_base import kb_service
    try:
        uid = int(user_id)
        results = await kb_service.search_similar(uid, query, top_k=3)
        if not results:
            return f"No RAG documents found matching '{query}'."
        return "\n".join([f"• Doc: {r['file_name']} (Relevance: {round(r['score']*100, 1)}%): \"{r['raw_text'][:150]}...\"" for r in results])
    except Exception as e:
        return f"Memory search error: {e}"

@registry.register("search_youtube_songs", "Searches YouTube for music tracks/songs. Requires 'query' string (e.g. 'Alan Walker Faded').")
async def search_youtube_songs_tool(query: str) -> str:
    from app.services.media_tools import media_tools
    results = await media_tools.search_youtube_songs(query, max_results=5)
    if not results:
        return f"No YouTube songs found matching '{query}'."
    formatted = []
    for idx, r in enumerate(results, 1):
        formatted.append(f"{idx}. {r['title']} — {r['uploader']} ({r['duration']})\n   URL: {r['url']}")
    return "\n\n".join(formatted)

