from pyrogram import filters
from pyrogram.types import Message

from AXL import app, LOGGER
from AXL.utils.queue_manager import queue_manager
from AXL.utils.player import (
    pause_playback,
    resume_playback,
    skip_current,
    stop_playback,
)
from AXL.utils.admins import is_admin_or_auth
from AXL.database import remove_active_chat


@app.on_message(filters.command("pause") & filters.group)
async def pause_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can pause playback.")
        return

    chat_id = message.chat.id
    if queue_manager.get_current(chat_id) is None:
        await message.reply_text("❌ Nothing is playing right now.")
        return

    success = await pause_playback(chat_id)
    if success:
        await message.reply_text("⏸ Paused the music.")
    else:
        await message.reply_text("❌ Couldn't pause. Is something actually playing?")


@app.on_message(filters.command("resume") & filters.group)
async def resume_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can resume playback.")
        return

    chat_id = message.chat.id
    success = await resume_playback(chat_id)
    if success:
        await message.reply_text("▶️ Resumed the music.")
    else:
        await message.reply_text("❌ Couldn't resume. Is the music paused?")


@app.on_message(filters.command(["skip", "next"]) & filters.group)
async def skip_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can skip tracks.")
        return

    chat_id = message.chat.id
    current = queue_manager.get_current(chat_id)
    if current is None:
        await message.reply_text("❌ Nothing is playing right now.")
        return

    await message.reply_text(f"⏭ Skipped **{current['title']}**")
    await skip_current(chat_id)

    next_song = queue_manager.get_current(chat_id)
    if next_song:
        await message.reply_text(f"▶️ Now playing: **{next_song['title']}**")


@app.on_message(filters.command(["stop", "end"]) & filters.group)
async def stop_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can stop playback.")
        return

    chat_id = message.chat.id
    await stop_playback(chat_id)
    await remove_active_chat(chat_id)
    await message.reply_text("⏹ Stopped playback and left the voice chat. Queue cleared.")


@app.on_message(filters.command(["queue", "q"]) & filters.group)
async def queue_command(client, message: Message):
    chat_id = message.chat.id
    current = queue_manager.get_current(chat_id)
    upcoming = queue_manager.get_queue(chat_id)

    if current is None:
        await message.reply_text("📭 Queue is empty and nothing is playing.")
        return

    text = f"🎶 **Now Playing:**\n{current['title']} ({current['duration']})\n\n"

    if upcoming:
        text += "📋 **Up Next:**\n"
        for i, song in enumerate(upcoming[:10], start=1):
            text += f"{i}. {song['title']} ({song['duration']})\n"
        if len(upcoming) > 10:
            text += f"\n...and {len(upcoming) - 10} more"
    else:
        text += "📭 No songs in queue."

    await message.reply_text(text)


@app.on_message(filters.command(["loop"]) & filters.group)
async def loop_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can toggle loop.")
        return

    chat_id = message.chat.id
    current_state = queue_manager.is_looping(chat_id)
    queue_manager.set_loop(chat_id, not current_state)

    if not current_state:
        await message.reply_text("🔁 Loop enabled - current track will repeat.")
    else:
        await message.reply_text("➡️ Loop disabled.")


@app.on_message(filters.command(["shuffle"]) & filters.group)
async def shuffle_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can shuffle the queue.")
        return

    chat_id = message.chat.id
    if queue_manager.queue_length(chat_id) < 2:
        await message.reply_text("❌ Not enough songs in queue to shuffle.")
        return

    queue_manager.shuffle_queue(chat_id)
    await message.reply_text("🔀 Queue shuffled!")


@app.on_message(filters.command(["remove"]) & filters.group)
async def remove_command(client, message: Message):
    if not await is_admin_or_auth(client, message):
        await message.reply_text("🚫 Only admins or authorized users can remove tracks.")
        return

    if len(message.command) < 2 or not message.command[1].isdigit():
        await message.reply_text("Usage: `/remove <position number>` (see /queue for positions)")
        return

    chat_id = message.chat.id
    index = int(message.command[1])
    success = queue_manager.remove_at_index(chat_id, index)

    if success:
        await message.reply_text(f"🗑 Removed track #{index} from queue.")
    else:
        await message.reply_text("❌ Invalid position. Check /queue for valid numbers.")
