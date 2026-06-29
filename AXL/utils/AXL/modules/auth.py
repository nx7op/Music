from pyrogram import filters
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from AXL import app
from AXL.database import add_auth_user, remove_auth_user, get_auth_users


async def _is_real_admin(client, chat_id: int, user_id: int) -> bool:
    try:
        member = await client.get_chat_member(chat_id, user_id)
        return member.status in (ChatMemberStatus.ADMINISTRATOR, ChatMemberStatus.OWNER)
    except Exception:
        return False


@app.on_message(filters.command("auth") & filters.group)
async def auth_command(client, message: Message):
    if not message.from_user or not await _is_real_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only group admins can authorize users.")
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except Exception:
            await message.reply_text("❌ Couldn't find that user.")
            return

    if not target:
        await message.reply_text("Reply to a user's message or provide a username/ID with `/auth`.")
        return

    await add_auth_user(message.chat.id, target.id)
    await message.reply_text(f"✅ {target.first_name} can now control music playback.")


@app.on_message(filters.command("unauth") & filters.group)
async def unauth_command(client, message: Message):
    if not message.from_user or not await _is_real_admin(client, message.chat.id, message.from_user.id):
        await message.reply_text("🚫 Only group admins can revoke authorization.")
        return

    target = None
    if message.reply_to_message and message.reply_to_message.from_user:
        target = message.reply_to_message.from_user
    elif len(message.command) > 1:
        try:
            target = await client.get_users(message.command[1])
        except Exception:
            await message.reply_text("❌ Couldn't find that user.")
            return

    if not target:
        await message.reply_text("Reply to a user's message or provide a username/ID with `/unauth`.")
        return

    await remove_auth_user(message.chat.id, target.id)
    await message.reply_text(f"✅ Removed {target.first_name}'s playback permissions.")


@app.on_message(filters.command("authlist") & filters.group)
async def authlist_command(client, message: Message):
    users = await get_auth_users(message.chat.id)
    if not users:
        await message.reply_text("📭 No authorized users in this group yet.")
        return

    text = "👥 **Authorized Users:**\n\n"
    for uid in users:
        try:
            u = await client.get_users(uid)
            text += f"• {u.first_name} (`{uid}`)\n"
        except Exception:
            text += f"• `{uid}`\n"

    await message.reply_text(text)
