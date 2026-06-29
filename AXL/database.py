from motor.motor_asyncio import AsyncIOMotorClient
from AXL.config import Config

_mongo_client = AsyncIOMotorClient(Config.MONGO_DB_URI)
db = _mongo_client["axl_music_bot"]

chats_col = db["chats"]
auth_users_col = db["auth_users"]
sudoers_col = db["sudoers"]
stats_col = db["stats"]


async def is_chat_active(chat_id: int) -> bool:
    chat = await chats_col.find_one({"chat_id": chat_id})
    return chat is not None


async def add_active_chat(chat_id: int):
    await chats_col.update_one(
        {"chat_id": chat_id}, {"$set": {"chat_id": chat_id}}, upsert=True
    )


async def remove_active_chat(chat_id: int):
    await chats_col.delete_one({"chat_id": chat_id})


async def get_all_active_chats():
    chats = []
    async for chat in chats_col.find({}):
        chats.append(chat["chat_id"])
    return chats


async def add_auth_user(chat_id: int, user_id: int):
    await auth_users_col.update_one(
        {"chat_id": chat_id, "user_id": user_id},
        {"$set": {"chat_id": chat_id, "user_id": user_id}},
        upsert=True,
    )


async def remove_auth_user(chat_id: int, user_id: int):
    await auth_users_col.delete_one({"chat_id": chat_id, "user_id": user_id})


async def is_auth_user(chat_id: int, user_id: int) -> bool:
    doc = await auth_users_col.find_one({"chat_id": chat_id, "user_id": user_id})
    return doc is not None


async def get_auth_users(chat_id: int):
    users = []
    async for doc in auth_users_col.find({"chat_id": chat_id}):
        users.append(doc["user_id"])
    return users


async def increment_play_count(chat_id: int):
    await stats_col.update_one(
        {"chat_id": chat_id},
        {"$inc": {"play_count": 1}},
        upsert=True,
    )


async def get_play_count(chat_id: int) -> int:
    doc = await stats_col.find_one({"chat_id": chat_id})
    if doc:
        return doc.get("play_count", 0)
    return 0
