import os
from dotenv import load_dotenv

load_dotenv()


def _get_int_list(env_value: str):
    if not env_value:
        return []
    cleaned = env_value.replace(",", " ")
    return [int(x) for x in cleaned.split() if x.strip().isdigit()]


class Config:
    API_ID = int(os.environ.get("API_ID", 0))
    API_HASH = os.environ.get("API_HASH", "")
    BOT_TOKEN = os.environ.get("BOT_TOKEN", "")
    ASSISTANT_SESSION = os.environ.get("ASSISTANT_SESSION", "")
    MONGO_DB_URI = os.environ.get("MONGO_DB_URI", "")
    OWNER_ID = _get_int_list(os.environ.get("OWNER_ID", "0"))
    SUDO_USERS = _get_int_list(os.environ.get("SUDO_USERS", ""))
    BOT_USERNAME = os.environ.get("BOT_USERNAME", "AxlMusicBot")
    BOT_NAME = os.environ.get("BOT_NAME", "AXL MUSIC BOT")
    SUPPORT_GROUP = os.environ.get("SUPPORT_GROUP", "")
    SUPPORT_CHANNEL = os.environ.get("SUPPORT_CHANNEL", "")
    MAX_QUEUE_SIZE = int(os.environ.get("MAX_QUEUE_SIZE", 20))
    AUTO_LEAVE_TIMEOUT = int(os.environ.get("AUTO_LEAVE_TIMEOUT", 300))
    DURATION_LIMIT_MIN = int(os.environ.get("DURATION_LIMIT_MIN", 60))
    LOG_GROUP_ID = int(os.environ.get("LOG_GROUP_ID") or 0)
    DOWNLOADS_DIR = "downloads"
