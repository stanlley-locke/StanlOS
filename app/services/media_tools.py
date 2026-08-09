import logging
import yt_dlp
import os
import asyncio
from pypdf import PdfReader
from pathlib import Path

logger = logging.getLogger(__name__)

import re

class MediaToolsService:
    def __init__(self):
        self.download_dir = Path("storage/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_media_audio(self, url: str) -> tuple[str, str, str]:
        """
        Downloads audio from YouTube, TikTok, Instagram, Twitter/X, SoundCloud, or direct media URLs.
        Returns tuple of (file_path, title, artist).
        """
        # Clean URL (e.g. youtu.be/xxx?si=yyy)
        yt_match = re.search(r'(?:youtu\.be/|youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            url = f"https://www.youtube.com/watch?v={yt_match.group(1)}"

        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_dir / '%(id)s.%(ext)s'),
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'extractor_args': {'youtube': ['client=ANDROID_MUSIC,ANDROID,IOS']}
        }
        
        cookie_path = str(Path("cookies.txt").absolute())
        if os.path.exists(cookie_path):
            ydl_opts['cookiefile'] = cookie_path

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                if not info:
                    return None, "Download failed or video unavailable.", "Unknown"
                title = info.get('title', 'Extracted Audio')
                artist = info.get('artist') or info.get('uploader') or info.get('channel') or info.get('creator') or 'StanlOS Media'
                vid = info.get('id', 'media')
                
                # Look for downloaded audio file
                downloaded_file = None
                
                # Best way: Check yt-dlp's requested_downloads
                requested = info.get('requested_downloads')
                if requested and len(requested) > 0:
                    downloaded_file = requested[0].get('filepath')
                
                if not downloaded_file or not os.path.exists(downloaded_file):
                    # Fallback to prepare_filename
                    expected = ydl.prepare_filename(info)
                    if expected and os.path.exists(expected):
                        downloaded_file = expected
                    else:
                        # Fallback to guessing
                        for ext in ['webm', 'm4a', 'opus', 'mp3', 'mp4']:
                            candidate = str(self.download_dir / f"{vid}.{ext}")
                            if os.path.exists(candidate):
                                downloaded_file = candidate
                                break
                        
                if not downloaded_file or not os.path.exists(downloaded_file):
                    return None, "Audio file not found.", artist
                    
                # Clean title for filesystem
                safe_title = re.sub(r'[^\w\s-]', '', title).strip()
                if not safe_title:
                    safe_title = f"audio_{vid}"
                clean_name = f"{safe_title}.mp3"
                target_mp3 = str(self.download_dir / clean_name)

                if downloaded_file.endswith('.mp3'):
                    if downloaded_file != target_mp3:
                        try:
                            os.rename(downloaded_file, target_mp3)
                        except Exception:
                            target_mp3 = downloaded_file
                    return target_mp3, title, artist

                # Convert to MP3 using ffmpeg CLI
                ffmpeg_bin = str(Path('storage/bin/ffmpeg').absolute())
                if not os.path.exists(ffmpeg_bin):
                    ffmpeg_bin = "ffmpeg"
                    
                cmd = f'"{ffmpeg_bin}" -y -i "{downloaded_file}" "{target_mp3}"'
                ret = os.system(cmd)
                if ret == 0 and os.path.exists(target_mp3):
                    try:
                        if downloaded_file != target_mp3:
                            os.remove(downloaded_file)
                    except Exception:
                        pass
                    return target_mp3, title, artist
                elif os.path.exists(downloaded_file):
                    return downloaded_file, title, artist
                return None, title, artist

        try:
            res_path, res_title, res_artist = await asyncio.to_thread(_download)
            return res_path, res_title, res_artist
        except Exception as e:
            logger.error(f"Error downloading media audio from {url}: {e}")
            return None, str(e), "Error"

    async def search_soundcloud_songs(self, query: str, max_results: int = 5, limit: int = 5) -> list[dict]:
        """
        Searches  for music tracks/songs using scsearch:<query>.
        """
        count = max_results if max_results != 5 else limit
        ydl_opts = {
            'default_search': 'scsearch',
            'nocheckcertificate': True,
            'ignoreerrors': True,
            'no_warnings': True,
            'quiet': True,
            'extract_flat': True,
        }
        
        def _search():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                res = ydl.extract_info(f"scsearch{count}:{query}", download=False)
                if not res or 'entries' not in res:
                    return []
                results = []
                for entry in res['entries']:
                    if not entry:
                        continue
                    url = entry.get('url')
                    if not url:
                        continue
                    dur_sec = entry.get('duration', 0) or 0
                    dur_str = f"{int(dur_sec // 60)}:{int(dur_sec % 60):02d}" if dur_sec else "N/A"
                    # We pass the full URL safely by storing it or using a shorter identifier if possible,
                    # but Soundcloud URLs are sometimes long. We will return the URL.
                    results.append({
                        'id': str(entry.get('id', '')),
                        'title': entry.get('title', 'Unknown Track'),
                        'url': url,
                        'uploader': entry.get('uploader') or 'Artist',
                        'duration': dur_str
                    })
                return results

        try:
            return await asyncio.to_thread(_search)
        except Exception as e:
            logger.error(f"Error searching SoundCloud for '{query}': {e}")
            return []

    async def extract_text_from_pdf(self, file_path: str) -> str:
        """
        Extracts text from a local PDF file.
        """
        def _extract():
            reader = PdfReader(file_path)
            text = ""
            for page in reader.pages:
                text += page.extract_text() + "\n"
            return text.strip()

        try:
            return await asyncio.to_thread(_extract)
        except Exception as e:
            logger.error(f"Error extracting PDF text: {e}")
            return ""

    async def get_youtube_title_oembed(self, url: str) -> str:
        """
        Uses YouTube's public oEmbed API to fetch the title of a YouTube video safely.
        """
        import urllib.request, json
        
        # Clean URL to base format
        yt_match = re.search(r'(?:youtu\.be/|youtube\.com/watch\?v=)([a-zA-Z0-9_-]{11})', url)
        if yt_match:
            clean_url = f"https://www.youtube.com/watch?v={yt_match.group(1)}"
        else:
            clean_url = url
            
        oembed_url = f"https://www.youtube.com/oembed?url={clean_url}&format=json"
        
        def _fetch():
            req = urllib.request.Request(oembed_url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=10) as response:
                data = json.loads(response.read().decode('utf-8'))
                return data.get('title', '')
                
        try:
            return await asyncio.to_thread(_fetch)
        except Exception as e:
            logger.error(f"Error fetching YouTube title via oEmbed: {e}")
            return ""

media_tools = MediaToolsService()
