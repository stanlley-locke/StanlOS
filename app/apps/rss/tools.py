import feedparser
import asyncio
from app.agent.tools import registry

@registry.register("get_latest_news", "Fetches latest real-time news headlines based on a topic (e.g. 'tech', 'business', 'world', 'ai').")
async def get_latest_news(topic: str = "world") -> str:
    feeds = {
        "tech": "https://techcrunch.com/feed/",
        "business": "http://feeds.bbci.co.uk/news/business/rss.xml",
        "world": "http://feeds.bbci.co.uk/news/world/rss.xml",
        "ai": "https://www.artificialintelligence-news.com/feed/"
    }
    
    target_feed = feeds.get(topic.lower(), feeds["world"])
    
    def _fetch():
        d = feedparser.parse(target_feed)
        entries = []
        for entry in d.entries[:5]:
            title = getattr(entry, 'title', 'No Title')
            link = getattr(entry, 'link', '')
            entries.append(f"• {title}\n  {link}")
        return "\n\n".join(entries) if entries else "No news found for this topic."
        
    try:
        return await asyncio.to_thread(_fetch)
    except Exception as e:
        return f"News feed error: {e}"
