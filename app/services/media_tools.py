import logging
import yt_dlp
import os
import asyncio
from pypdf import PdfReader
from pathlib import Path

logger = logging.getLogger(__name__)

class MediaToolsService:
    def __init__(self):
        self.download_dir = Path("storage/downloads")
        self.download_dir.mkdir(parents=True, exist_ok=True)

    async def download_youtube_audio(self, url: str) -> str:
        """
        Downloads audio from a YouTube video and returns the file path.
        """
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': str(self.download_dir / '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'quiet': True
        }

        def _download():
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                info = ydl.extract_info(url, download=True)
                # yt-dlp changes extension to mp3 after postprocessing
                return ydl.prepare_filename(info).rsplit('.', 1)[0] + '.mp3'

        try:
            return await asyncio.to_thread(_download)
        except Exception as e:
            logger.error(f"Error downloading YouTube audio: {e}")
            return None

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

media_tools = MediaToolsService()
