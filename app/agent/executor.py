import logging
import json
from typing import List, Dict, Callable, Awaitable

from app.services.ai_cloudflare import ai_client
from app.agent.tools import registry
from app.utils.formatters import safe_html, SYMBOLS

logger = logging.getLogger(__name__)

REACT_SYSTEM_PROMPT = """You are StanlOS, an advanced autonomous AI system assistant.
You operate using a strict ReAct (Reason-Act) loop.

Available Tools:
{tools}

Instructions:
- Use specific domain tools (e.g. 'log_expense', 'log_income', 'add_task', 'delete_task', 'clear_tasks', 'complete_task', 'add_contact', 'search_memory', 'search_youtube_songs', 'get_weather', 'search_web') to execute tasks directly.
- TASK DELETION RULE: To delete, remove, or clear tasks, use 'delete_task' or 'clear_tasks'. DO NOT call 'add_task' when asked to delete or cancel tasks!
- CRITICAL: DO NOT call 'userbot_send' or 'userbot_read' to deliver answers to the current user. To answer the user or present search/tool results, set "action": "Final Answer" and put your response in "action_input": {{"answer": "..."}}.
- ALWAYS respond in RAW JSON ONLY. NO MARKDOWN BLOCKS (` ```json `), NO EXPLANATIONS OUTSIDE JSON.

JSON Format:
{{
  "thought": "Reasoning about the task and tool to use.",
  "action": "Exact tool name (or 'Final Answer' when done)",
  "action_input": {{"key": "value"}}
}}
"""

class AgentExecutor:
    async def run(self, user_query: str, user_id: int = None, status_callback: Callable[[str], Awaitable[None]] = None) -> str:
        """
        Runs the ReAct loop until a final answer is reached or max iterations hit.
        """
        max_iterations = 10
        
        system_prompt = REACT_SYSTEM_PROMPT.format(tools=registry.get_tool_prompt())
        
        user_context = f"Current User Telegram ID: {user_id}\nUser Request: {user_query}" if user_id else user_query
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_context}
        ]
        
        last_tool_observation = ""
        
        for i in range(max_iterations):
            logger.info(f"Agent Loop Iteration {i+1}")
            
            # 1. Get AI reasoning and action
            response_json = await ai_client.generate_json(messages)
            
            if not response_json or not isinstance(response_json, dict):
                if last_tool_observation:
                    return last_tool_observation
                return "Task processed successfully."
                
            thought = response_json.get("thought", "Analyzing request...")
            action = response_json.get("action")
            action_input = response_json.get("action_input", {})
            
            if not isinstance(action_input, dict):
                action_input = {"answer": str(action_input)}

            # Inject user_id if tool requires it and model passed placeholder or omitted
            if user_id:
                if "user_id" in action_input and str(action_input["user_id"]).startswith(("your_", "user_", "none", "0")):
                    action_input["user_id"] = user_id
                elif "user_id" not in action_input:
                    action_input["user_id"] = user_id
            
            if status_callback and action and action != "Final Answer":
                status_text = (
                    f"⚡ <b>STANLOS AGENT STATUS</b>\n\n"
                    f"<b>Thought :</b> <i>{safe_html(thought)}</i>\n"
                    f"<b>Action  :</b> <code>{safe_html(str(action))}</code>"
                )
                await status_callback(status_text)
                
            if action == "Final Answer" or not action or str(action).lower() in ["none", "null", "done", "finish"]:
                ans = action_input.get("answer") or action_input.get("result") or action_input.get("input") or thought
                if ans and str(ans).strip() not in ["Thinking...", "Analyzing request...", "Generated response"]:
                    return str(ans)
                if last_tool_observation:
                    return last_tool_observation
                return str(ans) if ans else "Task completed successfully."
                
            # 2. Execute Tool
            tool_result = await registry.execute(action, **action_input)
            last_tool_observation = str(tool_result) if tool_result is not None else ""
            
            # 3. Append to context and loop
            messages.append({"role": "assistant", "content": json.dumps(response_json)})
            messages.append({"role": "user", "content": f"Observation from {action}:\n{tool_result}"})
            
        return last_tool_observation or "Agent processing completed."

agent = AgentExecutor()
