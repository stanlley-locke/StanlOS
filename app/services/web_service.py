import aiohttp
import logging
from bs4 import BeautifulSoup
import re
from typing import List, Dict

logger = logging.getLogger(__name__)

class WebService:
    def __init__(self):
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }

    async def search_duckduckgo(self, query: str, num_results: int = 5) -> List[Dict[str, str]]:
        """
        Scrape DuckDuckGo HTML for search results without an API key.
        """
        url = "https://html.duckduckgo.com/html/"
        data = {"q": query}
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, data=data, headers=self.headers) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    results = []
                    for a in soup.find_all('a', class_='result__snippet', limit=num_results):
                        snippet = a.get_text(strip=True)
                        link = a.get('href')
                        results.append({"url": link, "snippet": snippet})
                    return results
        except Exception as e:
            logger.error(f"DuckDuckGo search error: {e}")
            return []

    async def extract_text_from_url(self, url: str) -> str:
        """
        Fetch HTML from URL and extract readable text.
        """
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url, headers=self.headers, timeout=10) as response:
                    html = await response.text()
                    soup = BeautifulSoup(html, 'html.parser')
                    
                    # Remove scripts and styles
                    for script in soup(["script", "style", "nav", "footer", "header"]):
                        script.extract()
                        
                    text = soup.get_text(separator=' ')
                    # Collapse whitespace
                    clean_text = re.sub(r'\s+', ' ', text).strip()
                    
                    # Return first 5000 chars to avoid blowing up context window
                    return clean_text[:5000]
        except Exception as e:
            logger.error(f"URL extraction error for {url}: {e}")
            return f"Error: Could not retrieve content from {url}."

web_service = WebService()
