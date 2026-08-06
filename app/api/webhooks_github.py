import logging
from fastapi import APIRouter, Request, Header, HTTPException
from app.core.config import settings
from app.bot.dispatcher import bot
from app.utils.formatters import SYMBOLS, safe_html

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/webhooks/github", tags=["GitHub Webhook"])

@router.post("")
async def github_webhook(request: Request, x_github_event: str = Header(default="push")):
    try:
        payload = await request.json()
    except Exception as e:
        logger.error(f"Invalid JSON in GitHub webhook: {e}")
        raise HTTPException(status_code=400, detail="Invalid payload")

    admin_id = settings.ADMIN_IDS[0] if settings.ADMIN_IDS else None
    if not admin_id:
        return {"status": "skipped", "reason": "No admin configured"}

    event_type = x_github_event.lower()
    
    if event_type == "push":
        repo_name = payload.get("repository", {}).get("full_name", "Unknown Repo")
        pusher = payload.get("pusher", {}).get("name", "Someone")
        ref = payload.get("ref", "").replace("refs/heads/", "")
        commits = payload.get("commits", [])
        
        text = (
            f"<b>{SYMBOLS['devops']} GITHUB PUSH EVENT</b>\n\n"
            f"<b>Repository:</b> <code>{safe_html(repo_name)}</code>\n"
            f"<b>Branch:</b> <code>{safe_html(ref)}</code>\n"
            f"<b>Pushed By:</b> {safe_html(pusher)}\n"
            f"<b>Commits ({len(commits)}):</b>\n"
        )
        for c in commits[:3]:
            text += f"• <code>{c.get('id', '')[:7]}</code> {safe_html(c.get('message', '').splitlines()[0])}\n"

    elif event_type == "issues":
        action = payload.get("action", "updated")
        issue = payload.get("issue", {})
        title = issue.get("title", "")
        url = issue.get("html_url", "")
        sender = payload.get("sender", {}).get("login", "")
        
        text = (
            f"<b>{SYMBOLS['alert']} GITHUB ISSUE {action.upper()}</b>\n\n"
            f"<b>Title:</b> {safe_html(title)}\n"
            f"<b>User:</b> {safe_html(sender)}\n"
            f"<b>URL:</b> <a href=\"{url}\">View Issue</a>"
        )
    elif event_type == "star":
        action = payload.get("action", "created")
        repo = payload.get("repository", {}).get("full_name", "")
        sender = payload.get("sender", {}).get("login", "")
        text = f"<b>⭐ NEW GITHUB STAR</b>\n\n<b>{safe_html(sender)}</b> {action} a star on <b>{safe_html(repo)}</b>!"
    else:
        text = f"<b>🔔 GITHUB EVENT: {event_type.upper()}</b>\n\nPayload received for {safe_html(payload.get('repository', {}).get('full_name', ''))}"

    try:
        await bot.send_message(admin_id, text, disable_web_page_preview=True)
    except Exception as e:
        logger.error(f"Failed to send GitHub notification to admin: {e}")

    return {"status": "ok", "event": event_type}
