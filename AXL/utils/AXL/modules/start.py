import time
import psutil
from pyrogram import filters
from pyrogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton

from AXL import app
from AXL.config import Config

START_TIME = time.time()

HELP_TEXT = """
🎵 **AXL MUSIC BOT - Commands**

**Playback:**
/play `<song name/link>` - Play a song
/pause - Pause current track
/resume - Resume playback
/skip - Skip current track
/stop - Stop and leave VC
/queue - Show current queue
/loop - Toggle loop for current track
/shuffle - Shuffle the queue
/remove `<position>` - Remove a track from queue

**Permissions (admins only):**
/auth `<reply or username>` - Allow a user to control music
/unauth `<reply or username>` - Revoke that permission
/authlist - List authorized users in this group

**Info:**
/start - Welcome message
/help - This message
/ping - Check bot responsiveness
/stats - Bot system stats
"""


@app.on_message(filters.command("start"))
async def start_command(client, message: Message):
    buttons = InlineKeyboardMarkup(
        [
            [
                InlineKeyboardButton("➕ Add me to your group", url=f"https://t.me/{Config.BOT_USERNAME}?startgroup=true"),
            ],
            [
                InlineKeyboardButton("📖 Help", callback_data="help_menu"),
            ],
        ]
    )

    await message.reply_text(
        f"👋 **Hi {message.from_user.first_name if message.from_user else ''}!**\n\n"
        f"I'm **{Config.BOT_NAME}** - an advanced voice chat music bot.\n\n"
        f"Add me to your group and start a voice chat, then use /play to start streaming music!\n\n"
        f"Use /help to see all my commands.",
        reply_markup=buttons,
    )


@app.on_message(filters.command("help"))
async def help_command(client, message: Message):
    await message.reply_text(HELP_TEXT)


@app.on_callback_query(filters.regex("help_menu"))
async def help_callback(client, callback_query):
    await callback_query.message.edit_text(HELP_TEXT)


@app.on_message(filters.command("ping"))
async def ping_command(client, message: Message):
    start = time.time()
    msg = await message.reply_text("🏓 Pinging...")
    end = time.time()
    ping_ms = round((end - start) * 1000, 2)
    await msg.edit_text(f"🏓 **Pong!**\n⏱ `{ping_ms} ms`")


@app.on_message(filters.command("stats"))
async def stats_command(client, message: Message):
    uptime_seconds = int(time.time() - START_TIME)
    hours, remainder = divmod(uptime_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    cpu = psutil.cpu_percent()
    ram = psutil.virtual_memory()

    await message.reply_text(
        f"📊 **Bot Stats**\n\n"
        f"⏱ Uptime: {hours}h {minutes}m {seconds}s\n"
        f"💻 CPU Usage: {cpu}%\n"
        f"🧠 RAM Usage: {ram.percent}% ({round(ram.used / (1024**2))}MB / {round(ram.total / (1024**2))}MB)\n"
    )
