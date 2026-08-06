import aiohttp
import logging
from typing import Dict, Any

from app.core.config import settings

logger = logging.getLogger(__name__)

class GitHubService:
    def __init__(self):
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
        }
        if settings.GITHUB_TOKEN:
            self.headers["Authorization"] = f"token {settings.GITHUB_TOKEN}"

    async def get_repo_info(self, owner: str, repo: str) -> str:
        """
        Fetches repository details.
        """
        url = f"{self.base_url}/repos/{owner}/{repo}"
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers) as response:
                    if response.status == 200:
                        data = await response.json()
                        desc = data.get("description", "No description")
                        stars = data.get("stargazers_count", 0)
                        language = data.get("language", "Unknown")
                        return f"Repo: {owner}/{repo}\nDescription: {desc}\nStars: {stars}\nLanguage: {language}"
                    else:
                        return f"GitHub Error: {response.status} - {await response.text()}"
        except Exception as e:
            logger.error(f"GitHub API Error: {e}")
            return f"Error connecting to GitHub: {e}"

github_service = GitHubService()
