from pyrogram import filters
from pyrogram.types import Message

from AXL import app, calls, LOGGER
from AXL.utils.queue_manager import queue_manager
from AXL.utils.youtube import (
    search_youtube,
    is_youtube_url,
    download_audio,
    check_duration_limit,
    cleanup_old_downloads,
)
from AXL.utils.player import play_song
from AXL.database import add_active_chat
from pytgcalls.exceptions import NoActiveGroupCall


@app.on_message(filters.command(["play", "p"]) & filters.group)
async def play_command(client, message: Message):
    if len(message.command) < 2:
        await message.reply_text(
            "🎵 **Usage:** `/play <song name or YouTube link>`\n\n"
            "Example: `/play Shape of You`"
        )
        return

    query = message.text.split(None, 1)[1]
    chat_id = message.chat.id

    status_msg = await message.reply_text(f"🔍 Searching for **{query}**...")

    try:
        video_info = await search_youtube(query)

        if not video_info:
            await status_msg.edit_text("❌ No results found for your search.")
            return

        if not check_duration_limit(video_info["duration"]):
            await status_msg.edit_text(
                f"❌ Track too long! Limit is set to a maximum duration.\n"
                f"Track duration: {video_info['duration']}"
            )
            return

        await status_msg.edit_text(f"⬇️ Downloading **{video_info['title']}**...")

        file_path = await download_audio(video_info["url"], video_info["id"])
        cleanup_old_downloads()

        song = {
            "title": video_info["title"],
            "duration": video_info["duration"],
            "file_path": file_path,
            "url": video_info["url"],
            "requested_by": message.from_user.first_name if message.from_user else "Someone",
        }

        current = queue_manager.get_current(chat_id)

        if current is None:
            try:
                await play_song(chat_id, song, is_first=True)
                await add_active_chat(chat_id)
                await status_msg.edit_text(
                    f"▶️ **Now Playing**\n\n"
                    f"🎵 {song['title']}\n"
                    f"⏱ Duration: {song['duration']}\n"
                    f"🙋 Requested by: {song['requested_by']}"
                )
            except NoActiveGroupCall:
                await status_msg.edit_text(
                    "❌ No active voice chat found!\n"
                    "Please start a voice chat in this group first, then try again."
                )
            except Exception as e:
                LOGGER.error(f"Play error in {chat_id}: {e}")
                await status_msg.edit_text(
                    "❌ Couldn't join the voice chat. Make sure:\n"
                    "1. A voice chat is active\n"
                    "2. The assistant account is a member of this group"
                )
        else:
            try:
                position = queue_manager.add_to_queue(chat_id, song)
                await status_msg.edit_text(
                    f"✅ **Added to Queue** (#{position})\n\n"
                    f"🎵 {song['title']}\n"
                    f"⏱ Duration: {song['duration']}\n"
                    f"🙋 Requested by: {song['requested_by']}"
                )
            except OverflowError:
                await status_msg.edit_text("❌ Queue is full! Try again after some songs finish.")

    except Exception as e:
        LOGGER.error(f"Unexpected error in play_command: {e}")
        await status_msg.edit_text(f"❌ An error occurred: `{str(e)[:200]}`")
