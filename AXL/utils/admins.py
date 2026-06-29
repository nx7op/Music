from pyrogram import Client
from pyrogram.types import Message
from pyrogram.enums import ChatMemberStatus

from AXL.config import Config
from AXL.database import is_auth_user


async def is_admin_or_auth(client: Client, message: Message) -> bool:
    user_id = message.from_user.id if message.from_user else None
    if user_id is None:
        return False

    if user_id in Config.OWNER_ID or user_id in Config.SUDO_USERS:
        return True

    if message.chat.id and message.chat.type.name in ("GROUP", "SUPERGROUP"):
        if await is_auth_user(message.chat.id, user_id):
            return True
        try:
            member = await client.get_chat_member(message.chat.id, user_id)
            return member.status in (
                ChatMemberStatus.ADMINISTRATOR,
                ChatMemberStatus.OWNER,
            )
        except Exception:
            return False

    return False


async def is_owner_or_sudo(user_id: int) -> bool:
    return user_id in Config.OWNER_ID or user_id in Config.SUDO_USERS
