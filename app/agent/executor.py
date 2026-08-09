import logging
import json
from typing import List, Dict, Callable, Awaitable

from app.services.ai_cloudflare import ai_client
from app.agent.tools import registry
from app.utils.formatters import safe_html, SYMBOLS

logger = logging.getLogger(__name__)

# Base Prompt Template
REACT_SYSTEM_PROMPT_TEMPLATE = """You are StanlOS, an advanced autonomous AI system assistant.
Role: {role_description}

Available Tools:
{tools}

Instructions:
- Use specific domain tools (e.g. 'log_expense', 'search_web') to execute tasks directly.
- TASK DELETION RULE: To delete, remove, or clear tasks, use 'delete_task' or 'clear_tasks'.
- CRITICAL: DO NOT call 'userbot_send' or 'userbot_read' to deliver answers to the current user. To answer the user, set "action": "Final Answer" and put your response in "action_input": {{"answer": "..."}}.
- ALWAYS respond in RAW JSON ONLY. NO MARKDOWN BLOCKS, NO EXPLANATIONS OUTSIDE JSON.

JSON Format:
{{
  "thought": "Reasoning about the task and tool to use.",
  "action": "Exact tool name (or 'Final Answer' when done)",
  "action_input": {{"key": "value"}}
}}
"""

ROLES = {
    "finance": {
        "description": "You are the Finance Agent. You strictly handle logging expenses, incomes, tracking budgets, and financial summaries.",
        "allowed_tools": ["log_expense", "log_income", "get_financial_summary", "search_transactions", "delete_transaction", "currency_converter", "crypto_tracker", "calculate", "get_stock_price"]
    },
    "research": {
        "description": "You are the Research Agent. You specialize in finding data on the web, reading URLs, deep scraping, and answering complex questions.",
        "allowed_tools": ["search_web", "read_url", "scrape_and_synthesize", "search_news", "wiki_search", "search_memory", "get_weather", "translate_text", "fetch_github_trending", "summarize_text"]
    },
    "general": {
        "description": "You are the General Operations Agent. You handle tasks, contacts, system stats, and general orchestration.",
        "allowed_tools": ["add_task", "list_tasks", "delete_task", "complete_task", "clear_tasks", "remember_fact", "recall_fact", "schedule_reminder", "get_system_stats", "search_songs", "download_song", "get_current_time", "unit_converter", "generate_qr_code"]
    }
}

class SwarmManager:
    async def run(self, user_query: str, user_id: int = None, status_callback: Callable[[str], Awaitable[None]] = None, chat_history: List[Dict] = None) -> str:
        # 1. Intent Classification
        routing_prompt = f"""
        Classify the intent of the following user query into one of three agents: 'finance', 'research', or 'general'.
        - finance: Money, budgets, expenses, income, crypto, conversions.
        - research: Web searching, scraping URLs, weather, wiki, deep questions.
        - general: Tasks, to-do lists, playing music, system stats, memory, or anything else.
        
        Respond with exactly ONE WORD: either finance, research, or general.
        Query: {user_query}
        """
        
        classification = await ai_client.generate_text([{"role": "user", "content": routing_prompt}])
        agent_type = "general"
        if classification:
            clean_class = classification.strip().lower()
            if "finance" in clean_class: agent_type = "finance"
            elif "research" in clean_class: agent_type = "research"
            
        logger.info(f"SwarmManager routed query to: {agent_type.upper()} Agent")
        
        if status_callback:
            await status_callback(f"🧠 <b>SWARM MANAGER</b>: Routing task to <code>{agent_type.upper()}</code> Agent...")
            
        # 2. Auto-RAG Background Search
        rag_context = None
        try:
            from app.services.knowledge_base import kb_service
            if user_id:
                rag_context = await kb_service.get_context_for_query(user_id, user_query)
        except Exception as e:
            logger.error(f"Auto-RAG failed: {e}")
            
        # 3. Execute via specialized agent
        executor = AgentExecutor(agent_type)
        
        # Inject RAG context into user query
        augmented_query = user_query
        if rag_context:
            augmented_query = f"Context from Memory:\n{rag_context}\n\nUser Query:\n{user_query}"
            
        return await executor.run(augmented_query, user_id, status_callback, chat_history)

class AgentExecutor:
    def __init__(self, agent_type: str = "general"):
        self.agent_type = agent_type
        
    async def run(self, user_query: str, user_id: int = None, status_callback: Callable[[str], Awaitable[None]] = None, chat_history: List[Dict] = None) -> str:
        max_iterations = 10
        role_config = ROLES.get(self.agent_type, ROLES["general"])
        
        # Filter tools
        allowed = role_config["allowed_tools"]
        filtered_tools = ""
        for t in registry.tool_descriptions:
            if t["name"] in allowed:
                filtered_tools += f"- {t['name']}: {t['description']}\n"
                
        system_prompt = REACT_SYSTEM_PROMPT_TEMPLATE.format(
            role_description=role_config["description"],
            tools=filtered_tools
        )
        
        user_context = f"Current User Telegram ID: {user_id}\nUser Request: {user_query}" if user_id else user_query
        
        messages = [
            {"role": "system", "content": system_prompt}
        ]
        
        if chat_history:
            messages.extend(chat_history)
            
        messages.append({"role": "user", "content": user_context})
        
        last_tool_observation = ""
        
        for i in range(max_iterations):
            logger.info(f"{self.agent_type.upper()} Agent Iteration {i+1}")
            
            response_json = await ai_client.generate_json(messages)
            if not response_json or not isinstance(response_json, dict):
                if not ai_client.account_id or not ai_client.api_token:
                    return f"{SYMBOLS['alert']} AI backend offline: Cloudflare API credentials missing."
                return last_tool_observation or "Agent reasoning failed or API timed out."
                
            thought = response_json.get("thought", "Analyzing...")
            action = response_json.get("action")
            action_input = response_json.get("action_input", {})
            
            if not isinstance(action_input, dict):
                action_input = {"answer": str(action_input)}

            if user_id:
                if "user_id" in action_input and str(action_input["user_id"]).startswith(("your_", "user_", "none", "0")):
                    action_input["user_id"] = user_id
                elif "user_id" not in action_input:
                    action_input["user_id"] = user_id
            
            if status_callback and action and action != "Final Answer":
                status_text = (
                    f"⚡ <b>{self.agent_type.upper()} AGENT</b>\n\n"
                    f"<b>Thought :</b> <i>{safe_html(thought)}</i>\n"
                    f"<b>Action  :</b> <code>{safe_html(str(action))}</code>"
                )
                await status_callback(status_text)
                
            if action == "Final Answer" or not action or str(action).lower() in ["none", "null", "done", "finish"]:
                ans = action_input.get("answer") or action_input.get("result") or thought
                if ans and str(ans).strip() not in ["Thinking...", "Analyzing request...", "Generated response"]:
                    return str(ans)
                return last_tool_observation or "Task completed successfully."
                
            # Verify tool is allowed
            if action not in allowed:
                tool_result = f"Error: {action} is not allowed for the {self.agent_type} agent."
            else:
                tool_result = await registry.execute(action, **action_input)
                
            last_tool_observation = str(tool_result) if tool_result is not None else ""
            
            messages.append({"role": "assistant", "content": json.dumps(response_json)})
            messages.append({"role": "user", "content": f"Observation from {action}:\n{tool_result}"})
            
        return last_tool_observation or "Agent processing completed."

agent = SwarmManager()
