import logging
import json
from typing import List, Dict, Callable, Awaitable

from app.services.ai_cloudflare import ai_client
from app.agent.tools import registry

logger = logging.getLogger(__name__)

REACT_SYSTEM_PROMPT = """You are StanlOS, an advanced autonomous AI agent.
You operate using a strict ReAct (Reason-Act) loop.

{tools}

You must ALWAYS respond in the following EXACT JSON format. NO MARKDOWN BLOCKS (` ```json `), NO EXPLANATIONS. ONLY RAW JSON.

{{
  "thought": "Your reasoning about what to do next.",
  "action": "The exact name of the tool to use (e.g. search_web), or 'Final Answer' if you are done.",
  "action_input": {{"key": "value"}} // The arguments for the tool, or {{"answer": "Your final response"}} if action is 'Final Answer'.
}}
"""

class AgentExecutor:
    async def run(self, user_query: str, status_callback: Callable[[str], Awaitable[None]] = None) -> str:
        """
        Runs the ReAct loop until a final answer is reached or max iterations hit.
        """
        max_iterations = 15
        
        system_prompt = REACT_SYSTEM_PROMPT.format(tools=registry.get_tool_prompt())
        
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_query}
        ]
        
        for i in range(max_iterations):
            logger.info(f"Agent Loop Iteration {i+1}")
            
            # 1. Get AI reasoning and action
            response_json = await ai_client.generate_json(messages)
            
            if not response_json:
                return "[ ! ] System Error: Agent loop terminated prematurely due to AI response failure."
                
            thought = response_json.get("thought", "Thinking...")
            action = response_json.get("action")
            action_input = response_json.get("action_input", {})
            
            if status_callback:
                await status_callback(f"<b>[ @ ] AGENT STATUS</b>\n<i>Thought:</i> {thought}\n<i>Action:</i> {action}")
                
            if action == "Final Answer" or not action:
                return action_input.get("answer", "No final answer provided.")
                
            # 2. Execute Tool
            tool_result = await registry.execute(action, **action_input)
            
            # 3. Append to context and loop
            # We append the AI's response as an assistant message
            messages.append({"role": "assistant", "content": json.dumps(response_json)})
            # We append the tool result as a user message (simulating tool observation)
            messages.append({"role": "user", "content": f"Observation from {action}:\n{tool_result}"})
            
        return "[ ! ] Agent hit maximum iterations without completing the task."

agent = AgentExecutor()
