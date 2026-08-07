import logging
from app.agent.tools import registry
from app.core.database import db

logger = logging.getLogger(__name__)

APPS_METADATA = [
    # Productivity
    {"id": "gmail", "name": "Gmail", "category": "Productivity", "auth": "OAuth2", "desc": "Send and read emails"},
    {"id": "google_calendar", "name": "Google Calendar", "category": "Productivity", "auth": "OAuth2", "desc": "Manage your schedule"},
    {"id": "notion", "name": "Notion", "category": "Productivity", "auth": "API Key", "desc": "Manage workspaces and notes"},
    {"id": "google_sheets", "name": "Google Sheets", "category": "Productivity", "auth": "OAuth2", "desc": "Read and write spreadsheets"},
    {"id": "google_drive", "name": "Google Drive", "category": "Productivity", "auth": "OAuth2", "desc": "Manage cloud files"},
    {"id": "google_docs", "name": "Google Docs", "category": "Productivity", "auth": "OAuth2", "desc": "Edit documents"},
    {"id": "google_tasks", "name": "Google Tasks", "category": "Productivity", "auth": "OAuth2", "desc": "Manage to-do lists"},
    {"id": "hubspot", "name": "HubSpot", "category": "Productivity", "auth": "API Key", "desc": "CRM and marketing"},
    {"id": "airtable", "name": "Airtable", "category": "Productivity", "auth": "API Key", "desc": "Relational databases"},
    {"id": "wrike", "name": "Wrike", "category": "Productivity", "auth": "OAuth2", "desc": "Project management"},
    {"id": "cal", "name": "Cal", "category": "Productivity", "auth": "API Key", "desc": "Meeting scheduling"},
    {"id": "canvas", "name": "Canvas", "category": "Productivity", "auth": "API Key", "desc": "LMS integration"},
    
    # Engineering & Dev
    {"id": "github", "name": "GitHub", "category": "Engineering", "auth": "OAuth2", "desc": "Source code management"},
    {"id": "bitbucket", "name": "Bitbucket", "category": "Engineering", "auth": "OAuth2", "desc": "Git repository management"},
    {"id": "supabase", "name": "Supabase", "category": "Engineering", "auth": "API Key", "desc": "Database and backend"},
    {"id": "jira", "name": "Jira", "category": "Engineering", "auth": "API Key", "desc": "Issue tracking"},
    {"id": "linear", "name": "Linear", "category": "Engineering", "auth": "API Key", "desc": "Issue tracking for fast teams"},
    
    # Communication
    {"id": "slack", "name": "Slack", "category": "Communication", "auth": "OAuth2", "desc": "Team messaging"},
    {"id": "slackbot", "name": "Slackbot", "category": "Communication", "auth": "OAuth2", "desc": "Automated Slack messaging"},
    {"id": "outlook", "name": "Outlook", "category": "Communication", "auth": "OAuth2", "desc": "Microsoft email and calendar"},
    {"id": "discord", "name": "Discord", "category": "Communication", "auth": "OAuth2", "desc": "Community chat"},
    
    # AI & Search
    {"id": "composio", "name": "Composio", "category": "AI", "auth": "No Auth", "desc": "App integration framework"},
    {"id": "composio_search", "name": "Composio Search", "category": "AI", "auth": "No Auth", "desc": "Search framework"},
    {"id": "perplexity", "name": "Perplexity AI", "category": "AI", "auth": "API Key", "desc": "AI search engine"},
    {"id": "serpapi", "name": "SerpApi", "category": "AI", "auth": "API Key", "desc": "Google Search API"},
    {"id": "firecrawl", "name": "Firecrawl", "category": "AI", "auth": "API Key", "desc": "Web scraping API"},
    {"id": "tavily", "name": "Tavily", "category": "AI", "auth": "API Key", "desc": "AI web search"},
    {"id": "code_interpreter", "name": "Code Interpreter", "category": "AI", "auth": "No Auth", "desc": "Python sandbox"},
    
    # Creative & Social
    {"id": "twitter", "name": "Twitter", "category": "Social", "auth": "OAuth2", "desc": "Social media"},
    {"id": "youtube", "name": "YouTube", "category": "Social", "auth": "OAuth2", "desc": "Video platform"},
    {"id": "reddit", "name": "Reddit", "category": "Social", "auth": "OAuth2", "desc": "Community forums"},
    {"id": "figma", "name": "Figma", "category": "Social", "auth": "API Key", "desc": "Design platform"}
]

def generate_tool_for_app(app_data: dict):
    """Dynamically generates an AI agent tool for a specific app."""
    app_id = app_data["id"]
    app_name = app_data["name"]
    desc = f"Interact with the {app_name} app. Use this tool when the user asks to perform an action on {app_name}. Requires 'user_id' (int) and 'query' (string)."
    
    async def dynamic_tool(user_id: int | str, query: str) -> str:
        try:
            uid = int(user_id)
            rows = await db.execute("SELECT status FROM user_apps WHERE user_id = ? AND app_id = ?", (uid, app_id), fetch=True)
            if not rows or rows[0][0] != 'active':
                return f"SYSTEM INSTRUCTION: The user has not configured the {app_name} app yet. Tell the user to go to the App Store in the Telegram menu to configure {app_name}."
            
            # Since this is a massive framework, the actual API calls for all 30 apps are stubbed.
            return f"SYSTEM INSTRUCTION: The {app_name} app is successfully connected! However, the specific action '{query}' is currently a stub in this framework. Inform the user that the integration is active but the specific action is pending implementation."
        except Exception as e:
            return f"Error interacting with {app_name}: {e}"
            
    # Set the function name dynamically so the registry accepts it nicely
    dynamic_tool.__name__ = f"use_{app_id}_app"
    
    # Register it
    registry.register(f"use_{app_id}_app", desc)(dynamic_tool)

def register_all_app_tools():
    for app in APPS_METADATA:
        # Don't overwrite manually defined apps if they exist
        generate_tool_for_app(app)

register_all_app_tools()
