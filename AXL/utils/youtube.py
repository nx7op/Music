import os
import asyncio
import re
from youtubesearchpython import VideosSearch
import yt_dlp

from AXL.config import Config

YOUTUBE_URL_PATTERN = re.compile(
    r"(?:https?://)?(?:www\.)?(?:youtube\.com|youtu\.be)/\S+"
)


def is_youtube_url(text: str) -> bool:
    return bool(YOUTUBE_URL_PATTERN.match(text.strip()))


async def search_youtube(query: str):
    loop = asyncio.get_event_loop()

    def _search():
        results = VideosSearch(query, limit=1).result()
        if not results["result"]:
            return None
        video = results["result"][0]
        return {
            "title": video["title"],
            "url": video["link"],
            "duration": video.get("duration", "Unknown"),
            "thumbnail": video["thumbnails"][-1]["url"] if video.get("thumbnails") else None,
            "channel": video.get("channel", {}).get("name", "Unknown"),
            "id": video["id"],
        }

    return await loop.run_in_executor(None, _search)


def _duration_to_minutes(duration_str: str) -> float:
    if not duration_str or duration_str == "Unknown":
        return 0
    parts = duration_str.split(":")
    parts = [int(p) for p in parts]
    if len(parts) == 2:
        minutes, seconds = parts
        return minutes + seconds / 60
    if len(parts) == 3:
        hours, minutes, seconds = parts
        return hours * 60 + minutes + seconds / 60
    return 0


def check_duration_limit(duration_str: str) -> bool:
    if Config.DURATION_LIMIT_MIN <= 0:
        return True
    return _duration_to_minutes(duration_str) <= Config.DURATION_LIMIT_MIN


async def download_audio(url: str, video_id: str) -> str:
    output_path = os.path.join(Config.DOWNLOADS_DIR, f"{video_id}.mp3")

    if os.path.exists(output_path):
        return output_path

    loop = asyncio.get_event_loop()

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": os.path.join(Config.DOWNLOADS_DIR, f"{video_id}.%(ext)s"),
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
        "quiet": True,
        "no_warnings": True,
        "noplaylist": True,
        "concurrent_fragment_downloads": 1,
    }

    def _download():
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([url])

    await loop.run_in_executor(None, _download)
    return output_path


def cleanup_old_downloads(max_files: int = 30):
    downloads_dir = Config.DOWNLOADS_DIR
    if not os.path.exists(downloads_dir):
        return

    files = [
        os.path.join(downloads_dir, f)
        for f in os.listdir(downloads_dir)
        if f.endswith(".mp3")
    ]
    if len(files) <= max_files:
        return

    files.sort(key=os.path.getmtime)
    files_to_delete = files[: len(files) - max_files]
    for f in files_to_delete:
        try:
            os.remove(f)
        except OSError:
            pass
