import os
import logging

from pyrogram import Client
from pytgcalls import PyTgCalls

from AXL.config import Config

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s - %(name)s - %(message)s",
    datefmt="%H:%M:%S",
)
logging.getLogger("pyrogram").setLevel(logging.WARNING)
logging.getLogger("pytgcalls").setLevel(logging.WARNING)

LOGGER = logging.getLogger("AXL")

os.makedirs(Config.DOWNLOADS_DIR, exist_ok=True)

app = Client(
    name="AXLBot",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    bot_token=Config.BOT_TOKEN,
    in_memory=True,
)

assistant = Client(
    name="AXLAssistant",
    api_id=Config.API_ID,
    api_hash=Config.API_HASH,
    session_string=Config.ASSISTANT_SESSION,
    in_memory=True,
)

calls = PyTgCalls(assistant)
